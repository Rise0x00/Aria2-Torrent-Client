if [ ! -d "venv" ]; then
    echo -e "Venv not found!"
    bash ./install.sh
fi
source venv/bin/activate
python3 main.py