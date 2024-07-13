import os
import requests
from bs4 import BeautifulSoup
import re
import csv

from tqdm import tqdm

apkfile = 'mydataset/apk'
url = 'https://apkpure.net/app'
version_p = r'<title>Download (.*?) ([\d.]+) APK for Android - Free and Safe Download</title>'
download_p = ''
download_size = 200
download_times = ''
policy_file = open('policy.txt', 'a')
def get_policy_url(package_name):
    google_url = f'https://play.google.com/store/apps/details?id={package_name}'
    response1 = requests.get(google_url)
    if response1.status_code == 200:
        soup1 = BeautifulSoup(response1.text, 'html.parser')
        pattern1 = r'<a aria-label="Privacy Policy (.*?) will open in a new window or tab.'
        policy_url_matches = re.findall(pattern1, str(soup1))
        if policy_url_matches:
            privacy_policy_url = policy_url_matches[0]
            print(policy_url_matches)
            '''if not getpolicyhtml.save_html(privacy_policy_url, f'mydataset/policy/{package_name}.html'):
                policy_file.write(package_name)
                policy_file.write('     ')
                return False'''
            policy_file.write(package_name)
            policy_file.write('     ')
            policy_file.write(privacy_policy_url)
            policy_file.write('\n')
            return True

    else:
        policy_file.write(package_name)
        policy_file.write('     ')
        policy_file.write('\n')
        return False

def if_english_app(url):
    if '%' in url:
        return False
    else:
        return True


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
}
apklist = []
with open('policy.txt', 'r') as file:
    for line in file:
        apklist.append(line.split()[0])
    file.close()

'''for file in os.listdir('mydataset/apk'):
    apklist.append(file.replace('.apk', '').split('_')[0])'''

pat = r'<a data-dt-cate="[^"]+" href="([^"]+)" title="[^"]+">'
urls = []
response = requests.get(url, headers=headers)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    matches = re.findall(pat, str(soup))
    for match in matches:
        urls.append(match)
print(urls)
pattern = r"https://apkpure\.net/.*?/download"
for i in range(10):
    for url in urls:
        response = requests.get(f'https://apkpure.net{url}', headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            matches = re.findall(pattern, str(soup))
            for match in matches:
                print(match)
                if not if_english_app(match):
                    print('not english app')
                    continue
                package = match.split('/')[4]
                if package in apklist:
                    print(f'exist {match}')
                    continue
                if '_' in package:
                    continue

                else:
                    r1 = requests.get(match, headers=headers)
                    if r1.status_code == 200:
                        soup = BeautifulSoup(r1.text, 'html.parser')

                        if 'd.apkpure.net/b/APK' not in str(soup):
                            print('this a xapk')
                            continue
                        if not get_policy_url(package):
                            print('this app not in google')
                            continue
                        matches = re.findall(r'takes up around (\d+\.\d+) MB of storage', str(soup))
                        matches1 = re.findall(r'takes up around (\d+\.\d+) GB of storage', str(soup))
                        if matches1:
                            continue
                        if matches:
                            number = float(matches[0])
                            if number > download_size:
                                continue
                            print(f'{number} MB')
                        match = re.search(version_p, str(soup))

                        if match:
                            version_number = match.group(2)
                            print(version_number)
                    else:

                        print('no')
                        continue
                    response = requests.get(f'https://d.apkpure.net/b/APK/{package}?version=latest', headers=headers, stream=True)
                    print('downloading... ')
                    if response.status_code == 200:

                        total_size = int(response.headers.get('content-length', 0))
                        block_size = 1024

                        save_filename = f"mydataset/apk/{package}_{version_number}_apk.apk"

                        with open(save_filename, 'wb') as f, tqdm(
                                desc=save_filename,
                                total=total_size,
                                unit='iB',
                                unit_scale=True,
                                unit_divisor=1024,
                        ) as bar:
                            for data in response.iter_content(block_size):
                                f.write(data)
                                bar.update(len(data))

                        print(f"File '{save_filename}' downloaded successfully.")
                        apklist.append(package)
                        break
                    else:
                        print(response.status_code)
                        print("Failed to download the file.")
        print(url)
        continue
