import aria2p
import time
import argparse
import subprocess
import atexit

def start_aria2_rpc():
    """Starts aria2c process with RPC server"""
    aria2_process = subprocess.Popen([
        "aria2c",
        "--enable-rpc",
        "--rpc-listen-port=6800",
        "--quiet",
        "--continue=true",
        "--seed-ratio=0.0",
        "--seed-time=0",
        "--allow-overwrite=true"
    ])
    return aria2_process

def cleanup(process):
    """Stops aria2c process on exit"""
    print("\nStopping aria2c...")
    process.terminate()

def main():
    # Parsing command line arguments
    parser = argparse.ArgumentParser(description='Torrent Downloader and Seeder')
    parser.add_argument('source', type=str, help='Magnet link or path to .torrent file')
    parser.add_argument('-d', '--directory', type=str, default='./downloads', 
                      help='Download directory (default: ./downloads)')
    args = parser.parse_args()

    # Starting aria2c process
    aria2_process = start_aria2_rpc()
    atexit.register(cleanup, aria2_process)

    # Initializing API client
    aria2 = aria2p.API(
        aria2p.Client(
            host="http://localhost",
            port=6800,
            secret=""
        )
    )

    # Giving time for RPC server to initialize
    time.sleep(1)

    # Adding download task
    try:
        if args.source.startswith('magnet:'):
            download = aria2.add_magnet(args.source, options={"dir": args.directory})
        elif args.source.endswith('.torrent'):
            download = aria2.add_torrent(args.source, options={"dir": args.directory})
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
            time.sleep(1)

        # Monitoring seeding process
        print("\n\nDownload complete! Starting to seed...")
        while True:
            download.update()
            print_seeding_stats(download)
            time.sleep(5)

    except KeyboardInterrupt:
        print("\n\nOperation terminated by user")

def print_progress(download):
    """Prints download progress"""
    progress = download.progress
    speed = download.download_speed_string()
    peers = download.connections
    size = download.total_length_string()
    status = f"Progress: {progress:.1f}% | Speed: {speed}/s | Peers: {peers} | Size: {size}"
    print(f"\r{status.ljust(80)}", end='')

def print_seeding_stats(download):
    """Prints seeding statistics"""
    uploaded = download.upload_length_string()
    speed = download.upload_speed_string()
    status = f"Seeding: Uploaded {uploaded} | Speed: {speed}/s"
    print(f"\r{status.ljust(80)}", end='')

if __name__ == "__main__":
    main()