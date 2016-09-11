#!/usr/bin/python3
import requests

print(requests.get('https://api.github.com/repos/Brachi/albam/releases/2877432').json()['assets'][0]['download_count'])
