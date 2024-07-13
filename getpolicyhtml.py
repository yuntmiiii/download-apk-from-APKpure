import os

import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
}
apk_policyurl = {

}

timeout = 10
def save_html(policy_url, filename):
    try:
        response = requests.get(policy_url, headers=headers, timeout=timeout)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f'save {package_name} as mydataset/policy/{package_name}.html')
        else:
            if policy_url.startswith('http:'):
                response = requests.get(policy_url.replace('http', 'https'), headers=headers)
                if response.status_code == 200:
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    print(f'save {package_name} as mydataset/policy/{package_name}.html')
                else:
                    print(f'{filename} no policy')
            else:
                print(f'{filename} no policy')

    except requests.exceptions.RequestException as e:
        print(f'Error downloading HTML: {e}')

with open('policy.txt', 'r') as file:
    for line in file:
        if len(line.split()) < 2:
            continue
        apk_policyurl[line.split()[0]] = line.split()[1]
    file.close()
for apk in os.listdir('mydataset/apk'):

    package_name = apk.replace('.apk', '').split('_')[0]
    if os.path.exists(rf'E:/SDK/mydataset/policy/{package_name}.html'):
        continue
    try:
        url = apk_policyurl[package_name]
    except:
        continue
    save_html(url, f'mydataset/policy/{package_name}.html')

