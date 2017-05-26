# Import
from lxml import html
import requests
import json
import csv
import sys

def floatify(num):
	try:
		x = float(num)
		return x
	except Exception as e:
		return num

# Base URL
base_url = "https://www.olympic.org"

# Get main page.
url = base_url + "/athletics"
response = requests.get(url)
tree = html.document_fromstring(response.text)

# Get all events.
sections = tree.xpath("//section[@class='sport-events ']")
events = []

# Iterate through events and extract.
for section in sections[0].xpath("div[@class='sport-event-col']"):

	for elements in section.xpath("div[@class='list-row']")[0]:

		for x in elements.xpath("li"):

			event = {
				"name": x.text_content().strip().title(),
				"url": base_url + "/" + x.xpath('a')[0].attrib['href'],
				"gender": "W" if "women" in x.text_content().strip() else "M",
			}

			response = requests.get(event["url"])
			tree = html.document_fromstring(response.text)

			event["games"] = []
			games = tree.xpath("//section[@class='event-box']")

			for game in games:

				name = game.xpath("h2")[0].text_content().strip()
				results = game.xpath("table")[0].xpath("tbody")[0].xpath("tr")

				event["games"].append({
					"location": name[:-5],
					"year": int(name[-4:]),
					"results": [{
						"medal": x.xpath("td")[0].xpath("div[contains(@class, 'medal')]")[0].text_content().strip(),
						"result": None if len(x.xpath("td")[0].xpath("span")) == 0 else floatify(x.xpath("td")[0].xpath("span")[0].text_content().strip()),
						"name": [ y.strip() for y in x.xpath("td")[1].xpath("div")[0].xpath("a")[0].xpath("div[@class='text-box']")[0].text_content().split("\r\n") if len(y.strip()) > 0 ][0] if len([ y.strip() for y in x.xpath("td")[1].xpath("div")[0].xpath("a")[0].xpath("div[@class='text-box']")[0].text_content().split("\r\n") if len(y.strip()) > 0 ]) == 2 else None,
						"nationality": [ y.strip() for y in x.xpath("td")[1].xpath("div")[0].xpath("a")[0].xpath("div[@class='text-box']")[0].text_content().split("\r\n") if len(y.strip()) > 0 ][1] if len([ y.strip() for y in x.xpath("td")[1].xpath("div")[0].xpath("a")[0].xpath("div[@class='text-box']")[0].text_content().split("\r\n") if len(y.strip()) > 0 ]) == 2 else [ y.strip() for y in x.xpath("td")[1].xpath("div")[0].xpath("a")[0].xpath("div[@class='text-box']")[0].text_content().split("\r\n") if len(y.strip()) > 0 ][0]
					} for x in results]
				})

			events.append(event)

# Write JSON
f = open("results.json", "w")
f.write(json.dumps(events, indent=4, sort_keys=True))
f.close()

import codecs

# Write CSV
f = codecs.open("results.csv", "a+", "utf-8")
f.write("Gender,Event,Location,Year,Medal,Name,Nationality,Result\n")

for event in events:

	for game in event["games"]:

		for result in game["results"]:

			f.write( ",".join([event["gender"], event["name"].encode("utf-8").strip(), game["location"], str(game["year"]), result["medal"], result["name"] or "null", result["nationality"], str(result["result"]) or "null"]) + "\n")

			# sys.exit()
			# print(",".join[ event["gender"], event["name"], event["url"], game["location"], game["year"], result["medal"], result["name"], result["nationality"], result["result"] ])

