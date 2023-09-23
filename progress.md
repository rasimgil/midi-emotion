# Stage 1, setting up the required files and credentials

First I have added the required files into the directory, namely the following:
- Lakh pianoroll 5 full dataset
- MSD summary file
- Lakh-MSD matching scores file
and placed them into ./data_files.

Later, obtained the client ID and client secret from https://developer.spotify.com/dashboard, where I have created a dummy app to get the credentials.

And filled them in src/create_dataset/utils.py

I created a virtual environment and installed the dependencies. I have removed the versions of the packages as their previous versions gave me problems.


Finally I ran src/create_dataset/run.py to create the dataset.

# Stage 2, problems

Initally, the first thing I realized how long the script would take. Here is a snippet of the first part of the output:

```
Adding metadata to each track in Lakh dataset
  0%|▎                                                                                                    | 3004/1000000 [03:31<17:59:11, 15.40it/s]
```

So I decided to first take a sample of the files, instead of getting all 1000000 files I ran it for 20 files only.

A bug manifested with the following output:

```
Adding metadata to each track in Lakh dataset
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████| 20/20 [00:01<00:00, 16.19it/s]
Mapping Echonest song IDs to Spotify song IDs
0it [00:00, ?it/s]
Traceback (most recent call last):
  File "C:\Users\erasi\OneDrive\Masaüstü\midi-emotion\src\create_dataset\run.py", line 135, in <module>
    data_already_processed = utils.read_csv(output_path_incomplete)
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\erasi\OneDrive\Masaüstü\midi-emotion\src\create_dataset\utils.py", line 215, in read_csv
    data = [{key: value for key, value in row.items()} for row in reader]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\erasi\OneDrive\Masaüstü\midi-emotion\src\create_dataset\utils.py", line 215, in <listcomp>
    data = [{key: value for key, value in row.items()} for row in reader]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\erasi\AppData\Local\Programs\Python\Python311\Lib\csv.py", line 118, in __next__
    row = next(self.reader)
          ^^^^^^^^^^^^^^^^^
  File "C:\Users\erasi\AppData\Local\Programs\Python\Python311\Lib\encodings\cp1252.py", line 23, in decode
    return codecs.charmap_decode(input,self.errors,decoding_table)[0]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeDecodeError: 'charmap' codec can't decode byte 0x90 in position 2886: character maps to <undefined>
Closing remaining open files:../../data_files/msd_summary_file.h5...done
```

Which resulted from the following line from the following read_csv method in utils.py:

```
def read_csv(input_file_path, delimiter=","):
    with open(input_file_path, "r") as f_in:
        reader = csv.DictReader(f_in, delimiter=delimiter)
        data = [{key: value for key, value in row.items()} for row in reader]
    return data
```

to fix the issue, I have added the encoding parameter to the open method:

```
def read_csv(input_file_path, delimiter=","):
    with open(input_file_path, "r", encoding="latin-1") as f_in:
        reader = csv.DictReader(f_in, delimiter=delimiter)
        data = [{key: value for key, value in row.items()} for row in reader]
    return data
```

