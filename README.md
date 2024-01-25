This project sends an email based on changes, warning or no changes in the Total Volumes of markets.
This folder is to be hosted on the ec2 instance. 

##### Set up the pre-requisites:
1. `sudo apt update` and `sudo apt-get update`
2. `sudo apt install unzip libnss3 python3-pip`
3. Set up the mozzila firefox software and webdrver for the project (chromedriver failed to run for Euro FX website):
`sudo apt-get install firefox`
and
```
sudo apt-get install firefox
sudo pip3 install selenium==3.0.2
sudo wget https://github.com/mozilla/geckodriver/releases/download/v0.29.1/geckodriver-v0.29.1-linux32.tar.gz -O /tmp/geckodriver.tar.gz \
  && sudo tar -C /opt -xzf /tmp/geckodriver.tar.gz \
  && sudo chmod 755 /opt/geckodriver \
  && sudo ln -fs /opt/geckodriver /usr/bin/geckodriver \
  && sudo ln -fs /opt/geckodriver /usr/local/bin/geckodriver
```
4. `sudo pip3 install -r requirements.txt`
5. `pip install -U selenium`	

<br> <br>

#### Steps to set up cron job:
Enter following commands in ubuntu/linux ec2 instanc:
1. Edit the cron file: `crontab -e`
2. Place following line in the file below which will open up: `00 23 * * * python3 /home/ubuntu/volume_scraping/main.py`
<br>
^ this script will run everyday at 2300h(GMT 0) AWS EC2 time which basically corresponds to 1700h USCT(GMT -5)
3. Save the file and exit and do whatever you want to because you shall be receiving emails on 1700h US CT.