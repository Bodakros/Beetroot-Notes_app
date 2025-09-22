with open("data.json", "r", encoding="utf-16") as f:
    content = f.read()

with open("data_n.json", "w", encoding="utf-8") as f:
    f.write(content)