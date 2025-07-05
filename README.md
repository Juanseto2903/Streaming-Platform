# 🎬 CineXtreem

This project was built as a practice platform for browsing and recommending movies. Users can explore a catalog and find top-rated films based on their average score — the best ones appear first.

You can also generate a kind of report that will show some graphics, stadistics and information from the csv movies, everything in a one PDF, and if you want you can send it via email to your friend, a random dude or even your boss¿?

Technologies used:
- **📱 PyQt6** for the GUI.
- **📃 Image formats** supported: PNG, JPG.
- **🖌️Font support**: TTF.
- **🎞️ Movie database**: CSV file.

Simply register as you would on any streaming platform and follow the instructions below to launch it 👍

## 📦 Installing dependencies

**🟦 Windows / 🍎 macOS**

```bash
# Install dependencies.
pip install -r requirements.txt
```
> Note: If the command does not work, you can force the installation using the following command: `py -m pip install requirements.txt`.

## 💻 Setup

```bash
# Clone the repository.
git clone https://github.com/Juanseto2903/Streaming-Platform

# Go to the repository.
cd Streaming-Platform
```

## 🔧 Initial Config

1. Create a `.env` file in the project root (Inside of "Streaming" folder, not outside) by copying the contents of `.env.example`.
2. Make sure you have MySQL running on your computer (for example, using XAMPP).
3. Have to change the info of `.env.example` to yours (or use the default, depends on yourself test it)

## 📚 Usage

Just run the main archive.

It will create the database and all the stuff you need to manage the info.
I mean:

Logs info, users, passwords, movies watched, among others.
Everything should be done.

Command(s): ⬇️

**👍 Recommended:**

```bash
# Use cd Streaming (to get into the main folder)
# And run this:
python Interfaz_Principal.py
```
Or could try this one just being in the repository:

```bash
python python Streaming\Interfaz_Principal.py
```

>Note: If the database doesn't create automatically, run the `Create_db.py` script to create the necessary database and tables.

```bash
python Streaming\Create_db.py
# Or just move with "cd" and run it.
```
> Note: If the database exists already, it won't create a new or another one.

Enjoy looking up your movies my lad 😌

## 🫂 Credits

This project was done with my university friends, now i'm updating and making some changes in it to set it better.
And because i need to practice my programming lol.

I'm really grateful to them and you will find their names (and mine too) at the beginning when you run the app btw.

## 📝 License

Copyright © 2025 [Juanseto2903](https://github.com/Juanseto2903).
This project is [MIT](LICENSE) licensed.

