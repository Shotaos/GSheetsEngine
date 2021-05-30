echo "creating virtual environment'
python -m venv myvenv
echo "installing packages in the virtual env"
".\myvenv\Scripts\activate" & pip install -r requirements.txt