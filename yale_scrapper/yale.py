import requests
import json


def get_department_urls(base_url):
    response = requests.get(base_url)
    data = json.loads(response.text)
    navigation_items = data['contextNavigation']['navigationItems']

    department_urls = {}
    for item in navigation_items:
        link = item['link']
        if '/myysm/people/people-by-department/' in link['url']:
            department_urls[link['text']] = link['url']

    return department_urls


url = "https://medicine.yale.edu/website-api-data/myysm/people/people-by-department/therapeutic-radiology/"
departments = get_department_urls(url)


def get_doctor_information(url):
    response = requests.get(url)
    data = json.loads(response.text)
    info = data['mainComponents'][0]['models']['members']['collection']


    result = []




    for item in info:
       result.append({
            "title": title,
            "forename": forename if type(forename) != type(list) else " ".join(forename),
            "surname": surname,
            "full_address": data.get("Practice Address", ""),
            "institution": data.get("Practice Name", ""),
            "department": data.get("Specialty", ""),
            "street": street,
            "city": city,
            "state": state,  # Using the state from CSV
            "postcode": pincode,
            "country": "United States",
            "specialty": data.get("Specialty", ""),
            "reg_number": "",
            "tel_1": data.get("Phone", ""),
            "tel_2": "",
            "tel_3": "",
            "fax_1": "",
            "fax_2": "",
            "fax_3": "",
            "mobile": "",
            "email_1": "",
            "email_2": "",
            "language": "",
            "gender": "",
            "workplace": data.get("Practice Name", ""),
            "website": data.get("Website", ""),
            "source_result_url": url
        })




