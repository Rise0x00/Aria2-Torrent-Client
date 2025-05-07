sudo apt update && sudo apt install aria2
pip3 install -r requirements.txt
read -p "Do you want to run software? (y/n): " choice
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    python3 main.py
fi