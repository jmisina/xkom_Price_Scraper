import pandas as pd
from bs4 import BeautifulSoup
import requests
from datetime import date
import os.path
import urllib.request



headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}
urlList = {"telefony":"https://www.x-kom.pl/g-4/c/1590-smartfony-i-telefony.html",
           "laptopy":"https://www.x-kom.pl/g-2/c/159-laptopy-notebooki-ultrabooki.html",
           "monitory":"https://www.x-kom.pl/g-6/c/15-monitory.html",
           "tablety":"https://www.x-kom.pl/g-2/c/1663-tablety.html",
           "gpu":"https://www.x-kom.pl/g-5/c/345-karty-graficzne.html",
           "hdd_zewn":"https://www.x-kom.pl/g-5/c/439-dyski-zewnetrzne-hdd.html",
           "ssd_wewn":"https://www.x-kom.pl/g-5/c/1779-dyski-ssd.html",
           "cpu":"https://www.x-kom.pl/g-5/c/11-procesory.html"}
parameterList = {"telefony":["Procesor", "Pamięć RAM", "Pamięć wbudowana", "Przekątna ekranu"],
                 "laptopy":["Procesor", "Pamięć RAM", "Przekątna ekranu", "Karta graficzna"],
                 "monitory":["Złącza", "Przekątna ekranu", "Rozdzielczość ekranu", "Czas reakcji"],
                 "tablety": ["Procesor", "Pamięć RAM", "Przekątna ekranu", "Rozdzielczość ekranu", "Typ ekranu", "System operacyjny"],
                 "gpu":["Pamięć", "Rodzaj pamięci", "Rodzaje wyjść"],
                 "hdd_zewn":["Pojemność", "Format", "Złącza", "Prędkość obrotowa"], # brak predkosci obrotowej na x-kom
                 "ssd_wewn":["Pojemność", "Format","Prędkość odczytu (maksymalna)","Prędkość zapisu (maksymalna)","Interfejs"],
                 "cpu":["Liczba rdzeni fizycznych", "Taktowanie rdzenia", "Gniazdo procesora (socket)"]}

for productType,url in urlList.items():
    result = requests.get(url, headers=headers)
    doc = BeautifulSoup(result.text, "html.parser")
    maxPage = int(doc.find_all("a", {"class": "sc-1h16fat-0 sc-1xy3kzh-0 gPKgJT"})[-1].getText())
    tempDF = pd.DataFrame()
    for pageNum in range(1, maxPage+1):
        newurl = url + "?page=" + str(pageNum)
        result = requests.get(newurl, headers=headers)
        doc = BeautifulSoup(result.text, "html.parser")
        prodNum = 1
        for productUrl in doc.find_all("a", {"class": "sc-1h16fat-0 sc-1yu46qn-7 bCpqs"}):
            tempUrl = "https://www.x-kom.pl"+productUrl['href']
            productPage = requests.get(tempUrl, headers=headers)
            productDoc = BeautifulSoup(productPage.text, "html.parser")
            try:
                nameblock = productDoc.find("div", {"class": "sc-1bker4h-10 kHPtVn"}).text

                brand, model = nameblock.split(" ", 1)
                model = model.split("(", 1)
                priceblock = productDoc.find("div", {"class": "sc-n4n86h-1 hYfBFq"})
                price = float(priceblock.text.replace(" zł", "").replace(",", ".").replace(" ", ""))
                tempDict = {"sklep": "x-kom", "nazwa": brand, "model": model[0], "cena": price}
                try:
                    parameterData = productDoc.find_all("div",
                                                        {"class": "sc-1s1zksu-0 sc-1s1zksu-1 hHQkLn sc-13p5mv-0 VGBov"})
                    for x in parameterData:
                        parameterTitle = x.find("div", {"class": "sc-1s1zksu-0 kmPqDP"}).text.strip()

                        if parameterTitle in parameterList[productType]:
                            parameterData = x.find("div", {"class": "sc-13p5mv-3 UfEQd"}).text
                            if parameterTitle == "Przekątna ekranu":
                                parameterData = float(parameterData.split('"')[0].replace(",", "."))
                            tempDict[parameterTitle] = parameterData
                except:
                    pass
            except:
                print(str(pageNum) + " / " + str(prodNum) + " " + "   Failed\n")

            tempDict["data"] = date.today().strftime("%Y.%m.%d")

            outDF = pd.DataFrame([tempDict])
            tempDF = pd.concat([tempDF, outDF], ignore_index=True)

            print(str(pageNum) + " / " + str(prodNum) + " " + nameblock.split("(", 1)[0] + "   Done\n")
            prodNum = prodNum + 1
        if os.path.isfile(productType + "_x-kom.csv"):
            tempDF.to_csv(productType + "_x-kom.csv", mode="a", index=False, encoding='utf-8-sig', sep=";", header="None")
        else:
            tempDF.to_csv(productType + "_x-kom.csv", mode="a", index=False, encoding='utf-8-sig', sep=";")

    print(productType + " Done\n")