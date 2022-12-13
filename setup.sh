envD="venvl"

if [ -d "$envD" ]; then
	rm -rf $envD
fi

python3 -m venv $envD --system-site-packages
. $envD/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -I -r requirements.txt
