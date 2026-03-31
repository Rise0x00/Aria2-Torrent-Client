if [ "$EUID" -ne 0 ]; then 
    echo -e "Warning: Script running without root privileges. Attempting to use sudo..."
    exec sudo "$0" "$@"
fi

apt update

apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    aria2

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

pip3 install --upgrade pip

if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "Error installing dependencies!$"
        exit 1
    fi
else
    echo -e "Warning: Requirements.txt file not found! Check where you're running the script."
fi

echo -e "Installation completed successfully!"

read -p "Do you want to run software? (y/[n]): " choice
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    python3 main.py
fi