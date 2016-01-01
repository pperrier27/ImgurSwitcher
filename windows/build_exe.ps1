# Powershell 5 script to automagically build the ImgurSwitcher exe 
$zipname = "ImgurSwitcher_amd64.zip"

# Delete everything in the dist directory
rm -Force -Recurse .\dist\*

# Execute setup script
cd ..\src
python py2exe_setup.py py2exe

# Create a zip file
cd ..\windows\dist
Compress-Archive -Path . -DestinationPath $zipname
cd ..