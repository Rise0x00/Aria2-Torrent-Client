import aria2p
import atexit
import subprocess
import os
import json
from time import sleep

def load_config():
    """Loads or creates configuration file with download and upload speed settings"""
    config_path = './config.json'
    default_config = {
        'max_download_speed': 0,  # 0 means no limit
        'max_upload_speed': 0     # 0 means no limit
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as config_file:
                config = json.load(config_file)
                print(f"Configuration loaded: download - {config.get('max_download_speed', 0)} KB/s, upload - {config.get('max_upload_speed', 0)} KB/s")
                return config
        except Exception as e:
            print(f"Error reading configuration file: {str(e)}")
            print("Creating configuration file with default parameters...")
    else:
        print("Configuration file not found! Creating new one with default parameters...")
    
    # Create default config file
    with open(config_path, 'w') as config_file:
        json.dump(default_config, config_file, indent=4)
    
    return default_config

def start_aria2_rpc(config):
    """Starts aria2c process with RPC server and speed settings from config"""
    max_download = config.get('max_download_speed', 0)
    max_upload = config.get('max_upload_speed', 0)
    
    cmd = [
        "aria2c",
        "--enable-rpc",
        "--rpc-listen-port=6800",
        "--quiet",
        "--continue=true",
        "--seed-ratio=0.0",
        "--seed-time=0",
        "--allow-overwrite=true"
    ]
    
    # Add speed limits if configured
    if max_download > 0:
        cmd.append(f"--max-download-limit={max_download}K")
    if max_upload > 0:
        cmd.append(f"--max-upload-limit={max_upload}K")
    
    aria2_process = subprocess.Popen(cmd)
    return aria2_process

def cleanup(process):
    print("\nStopping aria2c...")
    process.terminate()

def main():
    source = input("Enter a magnet link or the path to a file.torrent: ").strip()
    directory = input("Enter the download folder (default is ./downloads): ").strip()
    if not directory:
        directory = "./downloads"

    # Load configuration
    config = load_config()

    # Starting aria2c process with config
    aria2_process = start_aria2_rpc(config)
    atexit.register(cleanup, aria2_process)

    # Initializing API client
    aria2 = aria2p.API(
        aria2p.Client(
            host="http://localhost",
            port=6800,
            secret=""
        )
    )
    sleep(3)

    # Adding download task
    try:
        if source.startswith('magnet:'):
            download = aria2.add_magnet(source, options={"dir": directory})
        elif source.endswith('.torrent'):
            download = aria2.add_torrent(source, options={"dir": directory})
        else:
            print("Invalid source. Please use a magnet link or .torrent file.")
            return
    except Exception as e:
        print(f"Error adding download: {str(e)}")
        return

    print(f"Download started: {download.name}")
    print("Press Ctrl+C to stop\n")

    try:
        # Monitoring download progress
        while not download.is_complete:
            download.update()
            print_progress(download)
            sleep(1)

        # Monitoring seeding process
        print("\n\nDownload complete! Starting to seed...")
        print("Press Ctrl+C to stop\n")
        while True:
            download.update()
            print_seeding_stats(download)
            sleep(1)

    except KeyboardInterrupt:
        print("\n\nOperation terminated by user")

def print_progress(download):
    """Prints download progress"""
    progress = download.progress
    speed = download.download_speed_string()
    peers = download.connections
    size = download.total_length_string()
    status = f"Progress: {progress:.1f}% | Speed: {speed} | Peers: {peers} | Size: {size}"
    print(f"\r{status.ljust(80)}", end='')

def print_seeding_stats(download):
    """Prints seeding statistics"""
    uploaded = download.upload_length_string()
    speed = download.upload_speed_string()
    status = f"Seeding: Uploaded {uploaded} | Speed: {speed}"
    print(f"\r{status.ljust(80)}", end='')

if __name__ == "__main__":
    main()