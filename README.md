# vkdocdownload

# First steps
```bash
  pip3 install -r requirements.txt
```

# :pencil2: Usage

### Help
```bash
  python3 vkdd.py --help
```

### Search without saving

```bash
  python3 vkdd.py [Query]
```

### Search with saving

```bash
  python3 vkdd.py -s [Query]
```

### Change settings file
> Default settings file: settings.ini

```bash
  python3 vkdd.py --settings [settings_file_name + .ini] [Query]
```

### Change save path
```bash
  python3 vkdd.py -s -p/--path [path] [Query]
```

### Sorting by extension
```bash
  python3 vkdd.py -e pdf jpeg.. [Query]
```
