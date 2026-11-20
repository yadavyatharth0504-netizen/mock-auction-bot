import asyncio
import json
import os
import sqlite3
import time
import uuid
from typing import Dict, List, Optional, Tuple
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from telegram.constants import ParseMode
from aiohttp import web

DATABASE_URL = os.getenv("DATABASE_URL", "")
PORT = int(os.getenv("PORT", "8080"))

# ==============================================================================
# CONFIGURATION
# ==============================================================================
BOT_TOKEN = "9130227931:AAEUsragF2zlDZIvy7fy9cH1dH_iJh-l_QQ"
SUPER_ADMIN_ID = 8535673930
DB_PATH = "auction_bot.db"

IPL_TEAMS = ["CSK", "MI", "RCB", "KKR", "SRH", "RR", "DC", "PBKS", "GT", "LSG"]
WPL_TEAMS = ["MI-W", "DC-W", "RCB-W", "UPW", "GG"]

# ==============================================================================
# EMBEDDED 338 PLAYERS DATA (250 IPL + 88 WPL — NO EXTERNAL FILE NEEDED!)
# ==============================================================================
EMBEDDED_PLAYERS = [
  {
    "id": 1,
    "name": "KL Rahul",
    "role": "Wicketkeeper",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 2,
    "set_name": "Indian WKs (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 2,
    "name": "Ishan Kishan",
    "role": "Wicketkeeper",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 2,
    "set_name": "Indian WKs (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 3,
    "name": "Dhruv Jurel",
    "role": "Wicketkeeper",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 2,
    "set_name": "Indian WKs (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 4,
    "name": "Jitesh Sharma",
    "role": "Wicketkeeper",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 2,
    "set_name": "Indian WKs (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 5,
    "name": "Rishabh Pant",
    "role": "Wicketkeeper",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 2,
    "set_name": "Indian WKs (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 6,
    "name": "Sanju Samson",
    "role": "Wicketkeeper",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 2,
    "set_name": "Indian WKs (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 7,
    "name": "MS Dhoni",
    "role": "Wicketkeeper",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 2,
    "set_name": "Indian WKs (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 8,
    "name": "Shreyas Iyer",
    "role": "Batter",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 1,
    "set_name": "Indian Batters (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 9,
    "name": "Suryakumar Yadav",
    "role": "Batter",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 1,
    "set_name": "Indian Batters (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 10,
    "name": "Yashasvi Jaiswal",
    "role": "Batter",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 1,
    "set_name": "Indian Batters (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 11,
    "name": "Sai Sudharsan",
    "role": "Batter",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 1,
    "set_name": "Indian Batters (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 12,
    "name": "Ruturaj Gaikwad",
    "role": "Batter",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 1,
    "set_name": "Indian Batters (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 13,
    "name": "Shubman Gill",
    "role": "Batter",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 1,
    "set_name": "Indian Batters (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 14,
    "name": "Prabhsimran Singh",
    "role": "Batter",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 1,
    "set_name": "Indian Batters (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 15,
    "name": "Priyansh Arya",
    "role": "Batter",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 1,
    "set_name": "Indian Batters (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 16,
    "name": "Ajinkya Rahane",
    "role": "Batter",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 1,
    "set_name": "Indian Batters (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 17,
    "name": "Rajat Patidar",
    "role": "Batter",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 1,
    "set_name": "Indian Batters (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 18,
    "name": "Virat Kohli",
    "role": "Batter",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 1,
    "set_name": "Indian Batters (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 19,
    "name": "Abhishek Sharma",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 3,
    "set_name": "Indian All-rounders (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 20,
    "name": "Hardik Pandya",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 3,
    "set_name": "Indian All-rounders (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 21,
    "name": "Riyan Parag",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 3,
    "set_name": "Indian All-rounders (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 22,
    "name": "Axar Patel",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 3,
    "set_name": "Indian All-rounders (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 23,
    "name": "Ravindra Jadeja",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 3,
    "set_name": "Indian All-rounders (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 24,
    "name": "Krunal Pandya",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 3,
    "set_name": "Indian All-rounders (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 25,
    "name": "Shivam Dube",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 3,
    "set_name": "Indian All-rounders (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 26,
    "name": "Prasidh Krishna",
    "role": "Bowler",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 4,
    "set_name": "Indian Bowlers (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 27,
    "name": "Jasprit Bumrah",
    "role": "Bowler",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 4,
    "set_name": "Indian Bowlers (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 28,
    "name": "Arshdeep Singh",
    "role": "Bowler",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 4,
    "set_name": "Indian Bowlers (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 29,
    "name": "Mohammed Siraj",
    "role": "Bowler",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 4,
    "set_name": "Indian Bowlers (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 30,
    "name": "Varun Chakravarthy",
    "role": "Bowler",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 4,
    "set_name": "Indian Bowlers (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 31,
    "name": "Kuldeep Yadav",
    "role": "Bowler",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 4,
    "set_name": "Indian Bowlers (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 32,
    "name": "Bhuvneshwar Kumar",
    "role": "Bowler",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 4,
    "set_name": "Indian Bowlers (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 33,
    "name": "Harshit Rana",
    "role": "Bowler",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 4,
    "set_name": "Indian Bowlers (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 34,
    "name": "Nicholas Pooran",
    "role": "Wicketkeeper",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 6,
    "set_name": "Foreign WKs (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 35,
    "name": "Jos Buttler",
    "role": "Wicketkeeper",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 6,
    "set_name": "Foreign WKs (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 36,
    "name": "Phil Salt",
    "role": "Wicketkeeper",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 6,
    "set_name": "Foreign WKs (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 37,
    "name": "Heinrich Klaasen",
    "role": "Wicketkeeper",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 6,
    "set_name": "Foreign WKs (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 38,
    "name": "Tristan Stubbs",
    "role": "Wicketkeeper",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 6,
    "set_name": "Foreign WKs (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 39,
    "name": "Sunil Narine",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 7,
    "set_name": "Foreign All-rounders (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 40,
    "name": "Aiden Markram",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 7,
    "set_name": "Foreign All-rounders (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 41,
    "name": "Marco Jansen",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 7,
    "set_name": "Foreign All-rounders (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 42,
    "name": "Marcus Stoinis",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 7,
    "set_name": "Foreign All-rounders (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 43,
    "name": "Romario Shepherd",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 7,
    "set_name": "Foreign All-rounders (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 44,
    "name": "Cameron Green",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 7,
    "set_name": "Foreign All-rounders (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 45,
    "name": "Rohit Sharma",
    "role": "Batter",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 1,
    "set_name": "Indian Batters (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 46,
    "name": "Mitchell Marsh",
    "role": "Batter",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 5,
    "set_name": "Foreign Batters (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 47,
    "name": "Travis Head",
    "role": "Batter",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 5,
    "set_name": "Foreign Batters (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 48,
    "name": "Tim David",
    "role": "Batter",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 5,
    "set_name": "Foreign Batters (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 49,
    "name": "Dewald Brevis",
    "role": "Batter",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 5,
    "set_name": "Foreign Batters (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 50,
    "name": "Pat Cummins",
    "role": "Bowler",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 8,
    "set_name": "Foreign Bowlers (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 51,
    "name": "Trent Boult",
    "role": "Bowler",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 8,
    "set_name": "Foreign Bowlers (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 52,
    "name": "Josh Hazlewood",
    "role": "Bowler",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 8,
    "set_name": "Foreign Bowlers (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 53,
    "name": "Noor Ahmad",
    "role": "Bowler",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 8,
    "set_name": "Foreign Bowlers (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 54,
    "name": "Kagiso Rabada",
    "role": "Bowler",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 8,
    "set_name": "Foreign Bowlers (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 55,
    "name": "Jofra Archer",
    "role": "Bowler",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 8,
    "set_name": "Foreign Bowlers (2 Cr)",
    "league": "IPL"
  },
  {
    "id": 56,
    "name": "Vaibhav Suryavanshi",
    "role": "Batter",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 9,
    "set_name": "Indian Batters (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 57,
    "name": "Tilak Varma",
    "role": "Batter",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 9,
    "set_name": "Indian Batters (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 58,
    "name": "Devdutt Padikkal",
    "role": "Batter",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 9,
    "set_name": "Indian Batters (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 59,
    "name": "Nehal Wadhera",
    "role": "Batter",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 9,
    "set_name": "Indian Batters (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 60,
    "name": "Naman Dhir",
    "role": "Batter",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 9,
    "set_name": "Indian Batters (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 61,
    "name": "Shashank Singh",
    "role": "Batter",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 9,
    "set_name": "Indian Batters (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 62,
    "name": "Angkrish Raghuvanshi",
    "role": "Batter",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 9,
    "set_name": "Indian Batters (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 63,
    "name": "Rinku Singh",
    "role": "Batter",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 9,
    "set_name": "Indian Batters (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 64,
    "name": "Ashutosh Sharma",
    "role": "Batter",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 9,
    "set_name": "Indian Batters (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 65,
    "name": "Ayush Mhatre",
    "role": "Batter",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 9,
    "set_name": "Indian Batters (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 66,
    "name": "Ramandeep Singh",
    "role": "Batter",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 9,
    "set_name": "Indian Batters (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 67,
    "name": "Aniket Verma",
    "role": "Batter",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 9,
    "set_name": "Indian Batters (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 68,
    "name": "Shubham Dubey",
    "role": "Batter",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 9,
    "set_name": "Indian Batters (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 69,
    "name": "Abhishek Porel",
    "role": "Wicketkeeper",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 10,
    "set_name": "Indian WKs & ARs (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 70,
    "name": "Urvil Patel",
    "role": "Wicketkeeper",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 10,
    "set_name": "Indian WKs & ARs (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 71,
    "name": "Nitish Kumar Reddy",
    "role": "Allrounder",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 10,
    "set_name": "Indian WKs & ARs (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 72,
    "name": "Washington Sundar",
    "role": "Allrounder",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 10,
    "set_name": "Indian WKs & ARs (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 73,
    "name": "Venkatesh Iyer",
    "role": "Allrounder",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 10,
    "set_name": "Indian WKs & ARs (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 74,
    "name": "Rahul Tewatia",
    "role": "Allrounder",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 10,
    "set_name": "Indian WKs & ARs (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 75,
    "name": "Ayush Badoni",
    "role": "Allrounder",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 10,
    "set_name": "Indian WKs & ARs (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 76,
    "name": "Vipraj Nigam",
    "role": "Allrounder",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 10,
    "set_name": "Indian WKs & ARs (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 77,
    "name": "Harsh Dubey",
    "role": "Allrounder",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 10,
    "set_name": "Indian WKs & ARs (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 78,
    "name": "Khaleel Ahmed",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 11,
    "set_name": "Indian Bowlers (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 79,
    "name": "Yash Dayal",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 11,
    "set_name": "Indian Bowlers (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 80,
    "name": "Deepak Chahar",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 11,
    "set_name": "Indian Bowlers (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 81,
    "name": "Vaibhav Arora",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 11,
    "set_name": "Indian Bowlers (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 82,
    "name": "Sai Kishore",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 11,
    "set_name": "Indian Bowlers (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 83,
    "name": "Digvesh Singh Rathi",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 11,
    "set_name": "Indian Bowlers (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 84,
    "name": "Harshal Patel",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 11,
    "set_name": "Indian Bowlers (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 85,
    "name": "Avesh Khan",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 11,
    "set_name": "Indian Bowlers (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 86,
    "name": "Yuzvendra Chahal",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 11,
    "set_name": "Indian Bowlers (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 87,
    "name": "Suyash Sharma",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 11,
    "set_name": "Indian Bowlers (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 88,
    "name": "Mukesh Kumar",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 11,
    "set_name": "Indian Bowlers (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 89,
    "name": "Shardul Thakur",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 11,
    "set_name": "Indian Bowlers (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 90,
    "name": "Tushar Deshpande",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 11,
    "set_name": "Indian Bowlers (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 91,
    "name": "Sandeep Sharma",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 11,
    "set_name": "Indian Bowlers (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 92,
    "name": "Mohammed Shami",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 11,
    "set_name": "Indian Bowlers (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 93,
    "name": "Sherfane Rutherford",
    "role": "Batter",
    "base_price": 1.0,
    "nationality": "Foreigner",
    "set": 12,
    "set_name": "Foreign Batters & WKs (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 94,
    "name": "Shimron Hetmyer",
    "role": "Batter",
    "base_price": 1.0,
    "nationality": "Foreigner",
    "set": 12,
    "set_name": "Foreign Batters & WKs (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 95,
    "name": "Glenn Phillips",
    "role": "Batter",
    "base_price": 1.0,
    "nationality": "Foreigner",
    "set": 12,
    "set_name": "Foreign Batters & WKs (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 96,
    "name": "David Miller",
    "role": "Batter",
    "base_price": 1.0,
    "nationality": "Foreigner",
    "set": 12,
    "set_name": "Foreign Batters & WKs (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 97,
    "name": "Pathum Nissanka",
    "role": "Batter",
    "base_price": 1.0,
    "nationality": "Foreigner",
    "set": 12,
    "set_name": "Foreign Batters & WKs (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 98,
    "name": "Ryan Rickelton",
    "role": "Wicketkeeper",
    "base_price": 1.0,
    "nationality": "Foreigner",
    "set": 12,
    "set_name": "Foreign Batters & WKs (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 99,
    "name": "Quinton de Kock",
    "role": "Wicketkeeper",
    "base_price": 1.0,
    "nationality": "Foreigner",
    "set": 12,
    "set_name": "Foreign Batters & WKs (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 100,
    "name": "Tim Seifert",
    "role": "Wicketkeeper",
    "base_price": 1.0,
    "nationality": "Foreigner",
    "set": 12,
    "set_name": "Foreign Batters & WKs (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 101,
    "name": "Will Jacks",
    "role": "Allrounder",
    "base_price": 1.0,
    "nationality": "Foreigner",
    "set": 13,
    "set_name": "Foreign ARs & Bowlers (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 102,
    "name": "Mitchell Santner",
    "role": "Allrounder",
    "base_price": 1.0,
    "nationality": "Foreigner",
    "set": 13,
    "set_name": "Foreign ARs & Bowlers (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 103,
    "name": "Akeal Hosein",
    "role": "Allrounder",
    "base_price": 1.0,
    "nationality": "Foreigner",
    "set": 13,
    "set_name": "Foreign ARs & Bowlers (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 104,
    "name": "Liam Livingstone",
    "role": "Allrounder",
    "base_price": 1.0,
    "nationality": "Foreigner",
    "set": 13,
    "set_name": "Foreign ARs & Bowlers (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 105,
    "name": "Sam Curran",
    "role": "Allrounder",
    "base_price": 1.0,
    "nationality": "Foreigner",
    "set": 13,
    "set_name": "Foreign ARs & Bowlers (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 106,
    "name": "Rashid Khan",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Foreigner",
    "set": 13,
    "set_name": "Foreign ARs & Bowlers (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 107,
    "name": "Mitchell Starc",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Foreigner",
    "set": 13,
    "set_name": "Foreign ARs & Bowlers (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 108,
    "name": "Nathan Ellis",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Foreigner",
    "set": 13,
    "set_name": "Foreign ARs & Bowlers (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 109,
    "name": "Matheesha Pathirana",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Foreigner",
    "set": 13,
    "set_name": "Foreign ARs & Bowlers (1 Cr)",
    "league": "IPL"
  },
  {
    "id": 110,
    "name": "Abdul Samad",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 20,
    "set_name": "Indian Batters (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 111,
    "name": "Shahrukh Khan",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 20,
    "set_name": "Indian Batters (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 112,
    "name": "Karun Nair",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 20,
    "set_name": "Indian Batters (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 113,
    "name": "Nitish Rana",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 20,
    "set_name": "Indian Batters (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 114,
    "name": "Sameer Rizvi",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 20,
    "set_name": "Indian Batters (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 115,
    "name": "Manish Pandey",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 20,
    "set_name": "Indian Batters (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 116,
    "name": "Himmat Singh",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 20,
    "set_name": "Indian Batters (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 117,
    "name": "S. Ravichandran",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 20,
    "set_name": "Indian Batters (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 118,
    "name": "Rahul Tripathi",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 20,
    "set_name": "Indian Batters (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 119,
    "name": "Prithvi Shaw",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 20,
    "set_name": "Indian Batters (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 120,
    "name": "Sahil Parakh",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 20,
    "set_name": "Indian Batters (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 121,
    "name": "Akshat Raghuwanshi",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 20,
    "set_name": "Indian Batters (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 122,
    "name": "Danish Malewar",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 20,
    "set_name": "Indian Batters (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 123,
    "name": "Aman Rao",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 20,
    "set_name": "Indian Batters (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 124,
    "name": "Sarfaraz Khan",
    "role": "Wicketkeeper",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 19,
    "set_name": "Indian Wicketkeepers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 125,
    "name": "Kartik Sharma",
    "role": "Wicketkeeper",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 19,
    "set_name": "Indian Wicketkeepers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 126,
    "name": "Robin Minz",
    "role": "Wicketkeeper",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 19,
    "set_name": "Indian Wicketkeepers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 127,
    "name": "Anuj Rawat",
    "role": "Wicketkeeper",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 19,
    "set_name": "Indian Wicketkeepers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 128,
    "name": "Kumar Kushagra",
    "role": "Wicketkeeper",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 19,
    "set_name": "Indian Wicketkeepers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 129,
    "name": "Vishnu Vinod",
    "role": "Wicketkeeper",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 19,
    "set_name": "Indian Wicketkeepers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 130,
    "name": "Tejasvi Dahiya",
    "role": "Wicketkeeper",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 19,
    "set_name": "Indian Wicketkeepers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 131,
    "name": "Aman Khan",
    "role": "Wicketkeeper",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 19,
    "set_name": "Indian Wicketkeepers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 132,
    "name": "Mukul Choudhary",
    "role": "Wicketkeeper",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 19,
    "set_name": "Indian Wicketkeepers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 133,
    "name": "Ravi Singh",
    "role": "Wicketkeeper",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 19,
    "set_name": "Indian Wicketkeepers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 134,
    "name": "Salil Arora",
    "role": "Wicketkeeper",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 19,
    "set_name": "Indian Wicketkeepers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 135,
    "name": "Shahbaz Ahmad",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 136,
    "name": "Manav Suthar",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 137,
    "name": "Arjun Tendulkar",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 138,
    "name": "Prashant Veer",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 139,
    "name": "Auqib Dar",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 140,
    "name": "Mangesh Yadav",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 141,
    "name": "Ramakrishna Ghosh",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 142,
    "name": "Ajay Mandal",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 143,
    "name": "Madhav Tiwari",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 144,
    "name": "Tripurana Vijay",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 145,
    "name": "Gurnoor Singh Brar",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 146,
    "name": "Nishant Sindhu",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 147,
    "name": "Arshin Kulkarni",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 148,
    "name": "Raj Angad Bawa",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 149,
    "name": "Harnoor Pannu",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 150,
    "name": "Musheer Khan",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 151,
    "name": "Pyla Avinash",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 152,
    "name": "Suryansh Shedge",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 153,
    "name": "Abhinandan Singh",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 154,
    "name": "Swapnil Singh",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 155,
    "name": "Daksh Kamra",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 156,
    "name": "Prashant Solanki",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 157,
    "name": "Sarthak Ranjan",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 158,
    "name": "Naman Tiwari",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 159,
    "name": "Atharva Ankolekar",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 160,
    "name": "Mayank Rawat",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 161,
    "name": "Satwik Deswal",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 162,
    "name": "Kanishk Chouhan",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 163,
    "name": "Vihaan Malhotra",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 164,
    "name": "Vicky Ostwal",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 165,
    "name": "Shivang Kumar",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 18,
    "set_name": "Indian Allrounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 166,
    "name": "T Natarajan",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 167,
    "name": "Ashwani Kumar",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 168,
    "name": "Jaydev Unadkat",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 169,
    "name": "Anshul Kamboj",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 170,
    "name": "Gurjapneet Singh",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 171,
    "name": "Arshad Khan",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 172,
    "name": "Zeeshan Ansari",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 173,
    "name": "Harpreet Brar",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 174,
    "name": "Prince Yadav",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 175,
    "name": "Ishant Sharma",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 176,
    "name": "Vijaykumar Vyshak",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 177,
    "name": "Yudhvir Singh",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 178,
    "name": "Akash Singh",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 179,
    "name": "Mayank Yadav",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 180,
    "name": "Umran Malik",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 181,
    "name": "Mohsin Khan",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 182,
    "name": "Mayank Markande",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 183,
    "name": "M Siddharth",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 184,
    "name": "Rasikh Dar",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 185,
    "name": "Mukesh Choudhary",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 186,
    "name": "Yash Thakur",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 187,
    "name": "Anukul Roy",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 188,
    "name": "Shreyas Gopal",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 189,
    "name": "Jayant Yadav",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 190,
    "name": "Raghu Sharma",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 191,
    "name": "Akash Deep",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 192,
    "name": "Kartik Tyagi",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 193,
    "name": "Rahul Chahar",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 194,
    "name": "Ravi Bishnoi",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 195,
    "name": "Ashok Sharma",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 196,
    "name": "Prithviraj Yarra",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 197,
    "name": "Mohammad Izhar",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 198,
    "name": "Vishal Nishad",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 199,
    "name": "Pravin Dubey",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 200,
    "name": "Vignesh Puthur",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 201,
    "name": "Sushant Mishra",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 202,
    "name": "Yash Raj Punja",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 203,
    "name": "Brijesh Sharma",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 204,
    "name": "Kuldeep Sen",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 205,
    "name": "Krains Fuletra",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 206,
    "name": "Praful Hinge",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 207,
    "name": "Amit Kumar",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 208,
    "name": "Onkar Tarmale",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 209,
    "name": "Sakib Hussain",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 210,
    "name": "Shivam Mavi",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 17,
    "set_name": "Indian Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 211,
    "name": "Tom Banton",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 16,
    "set_name": "Foreign WKs & Batters (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 212,
    "name": "Jordan Cox",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 16,
    "set_name": "Foreign WKs & Batters (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 213,
    "name": "Jacob Bethell",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 16,
    "set_name": "Foreign WKs & Batters (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 214,
    "name": "Matthew Breetzke",
    "role": "Wicketkeeper",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 16,
    "set_name": "Foreign WKs & Batters (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 215,
    "name": "Donovan Ferreira",
    "role": "Wicketkeeper",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 16,
    "set_name": "Foreign WKs & Batters (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 216,
    "name": "Finn Allen",
    "role": "Wicketkeeper",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 16,
    "set_name": "Foreign WKs & Batters (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 217,
    "name": "Josh Inglis",
    "role": "Wicketkeeper",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 16,
    "set_name": "Foreign WKs & Batters (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 218,
    "name": "Ben Duckett",
    "role": "Wicketkeeper",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 16,
    "set_name": "Foreign WKs & Batters (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 219,
    "name": "Jamie Overton",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 15,
    "set_name": "Foreign All-rounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 220,
    "name": "Rachin Ravindra",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 15,
    "set_name": "Foreign All-rounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 221,
    "name": "Azmatullah Omarzai",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 15,
    "set_name": "Foreign All-rounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 222,
    "name": "Kamindu Mendis",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 15,
    "set_name": "Foreign All-rounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 223,
    "name": "Rovman Powell",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 15,
    "set_name": "Foreign All-rounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 224,
    "name": "Mitchell Owen",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 15,
    "set_name": "Foreign All-rounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 225,
    "name": "Matthew Short",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 15,
    "set_name": "Foreign All-rounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 226,
    "name": "Zac Foulkes",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 15,
    "set_name": "Foreign All-rounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 227,
    "name": "Jason Holder",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 15,
    "set_name": "Foreign All-rounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 228,
    "name": "Wanindu Hasaranga",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 15,
    "set_name": "Foreign All-rounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 229,
    "name": "Cooper Connolly",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 15,
    "set_name": "Foreign All-rounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 230,
    "name": "Ben Dwarshuis",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 15,
    "set_name": "Foreign All-rounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 231,
    "name": "Jack Edwards",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 15,
    "set_name": "Foreign All-rounders (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 232,
    "name": "Eshan Malinga",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 14,
    "set_name": "Foreign Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 233,
    "name": "Corbin Bosch",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 14,
    "set_name": "Foreign Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 234,
    "name": "Xavier Bartlett",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 14,
    "set_name": "Foreign Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 235,
    "name": "Lockie Ferguson",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 14,
    "set_name": "Foreign Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 236,
    "name": "Dushmantha Chameera",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 14,
    "set_name": "Foreign Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 237,
    "name": "Kwena Maphaka",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 14,
    "set_name": "Foreign Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 238,
    "name": "Nandre Burger",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 14,
    "set_name": "Foreign Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 239,
    "name": "Allah Ghazanfar",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 14,
    "set_name": "Foreign Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 240,
    "name": "Lhuan-dre Pretorius",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 14,
    "set_name": "Foreign Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 241,
    "name": "Nuwan Thushara",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 14,
    "set_name": "Foreign Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 242,
    "name": "Brydon Carse",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 14,
    "set_name": "Foreign Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 243,
    "name": "Mustafizur Rahman",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 14,
    "set_name": "Foreign Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 244,
    "name": "Matt Henry",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 14,
    "set_name": "Foreign Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 245,
    "name": "Lungi Ngidi",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 14,
    "set_name": "Foreign Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 246,
    "name": "Kyle Jamieson",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 14,
    "set_name": "Foreign Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 247,
    "name": "Luke Wood",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 14,
    "set_name": "Foreign Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 248,
    "name": "Anrich Nortje",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 14,
    "set_name": "Foreign Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 249,
    "name": "Adam Milne",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 14,
    "set_name": "Foreign Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 250,
    "name": "Jacob Duffy",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 14,
    "set_name": "Foreign Bowlers (0.5 Cr)",
    "league": "IPL"
  },
  {
    "id": 301,
    "name": "Sophie Devine",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 1,
    "set_name": "WPL Foreign All-rounders (2 Cr)",
    "league": "WPL"
  },
  {
    "id": 302,
    "name": "Nadine de Klerk",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 1,
    "set_name": "WPL Foreign All-rounders (2 Cr)",
    "league": "WPL"
  },
  {
    "id": 303,
    "name": "Nat Sciver-Brunt",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 1,
    "set_name": "WPL Foreign All-rounders (2 Cr)",
    "league": "WPL"
  },
  {
    "id": 304,
    "name": "Marizanne Kapp",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 1,
    "set_name": "WPL Foreign All-rounders (2 Cr)",
    "league": "WPL"
  },
  {
    "id": 305,
    "name": "Chinelle Henry",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 1,
    "set_name": "WPL Foreign All-rounders (2 Cr)",
    "league": "WPL"
  },
  {
    "id": 306,
    "name": "Georgia Wareham",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 1,
    "set_name": "WPL Foreign All-rounders (2 Cr)",
    "league": "WPL"
  },
  {
    "id": 307,
    "name": "Grace Harris",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 1,
    "set_name": "WPL Foreign All-rounders (2 Cr)",
    "league": "WPL"
  },
  {
    "id": 308,
    "name": "Ellyse Perry",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 1,
    "set_name": "WPL Foreign All-rounders (2 Cr)",
    "league": "WPL"
  },
  {
    "id": 309,
    "name": "Ashleigh Gardner",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 1,
    "set_name": "WPL Foreign All-rounders (2 Cr)",
    "league": "WPL"
  },
  {
    "id": 310,
    "name": "Amelia Kerr",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 1,
    "set_name": "WPL Foreign All-rounders (2 Cr)",
    "league": "WPL"
  },
  {
    "id": 311,
    "name": "Annabel Sutherland",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 1,
    "set_name": "WPL Foreign All-rounders (2 Cr)",
    "league": "WPL"
  },
  {
    "id": 312,
    "name": "Hayley Matthews",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 1,
    "set_name": "WPL Foreign All-rounders (2 Cr)",
    "league": "WPL"
  },
  {
    "id": 313,
    "name": "Beth Mooney",
    "role": "Wicketkeeper",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 2,
    "set_name": "WPL Foreign Stars (1-2 Cr)",
    "league": "WPL"
  },
  {
    "id": 314,
    "name": "Phoebe Litchfield",
    "role": "Batter",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 2,
    "set_name": "WPL Foreign Stars (1-2 Cr)",
    "league": "WPL"
  },
  {
    "id": 315,
    "name": "Laura Wolvaardt",
    "role": "Batter",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 2,
    "set_name": "WPL Foreign Stars (1-2 Cr)",
    "league": "WPL"
  },
  {
    "id": 316,
    "name": "Meg Lanning",
    "role": "Batter",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 2,
    "set_name": "WPL Foreign Stars (1-2 Cr)",
    "league": "WPL"
  },
  {
    "id": 317,
    "name": "Lauren Bell",
    "role": "Bowler",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 2,
    "set_name": "WPL Foreign Stars (1-2 Cr)",
    "league": "WPL"
  },
  {
    "id": 318,
    "name": "Sophie Ecclestone",
    "role": "Bowler",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 2,
    "set_name": "WPL Foreign Stars (1-2 Cr)",
    "league": "WPL"
  },
  {
    "id": 319,
    "name": "Shabnim Ismail",
    "role": "Bowler",
    "base_price": 2.0,
    "nationality": "Foreigner",
    "set": 2,
    "set_name": "WPL Foreign Stars (1-2 Cr)",
    "league": "WPL"
  },
  {
    "id": 320,
    "name": "Nicola Carey",
    "role": "Allrounder",
    "base_price": 1.0,
    "nationality": "Foreigner",
    "set": 2,
    "set_name": "WPL Foreign Stars (1-2 Cr)",
    "league": "WPL"
  },
  {
    "id": 321,
    "name": "Sophie Molineux",
    "role": "Allrounder",
    "base_price": 1.0,
    "nationality": "Foreigner",
    "set": 2,
    "set_name": "WPL Foreign Stars (1-2 Cr)",
    "league": "WPL"
  },
  {
    "id": 322,
    "name": "Jess Jonassen",
    "role": "Allrounder",
    "base_price": 1.0,
    "nationality": "Foreigner",
    "set": 2,
    "set_name": "WPL Foreign Stars (1-2 Cr)",
    "league": "WPL"
  },
  {
    "id": 323,
    "name": "Georgia Voll",
    "role": "Batter",
    "base_price": 1.0,
    "nationality": "Foreigner",
    "set": 2,
    "set_name": "WPL Foreign Stars (1-2 Cr)",
    "league": "WPL"
  },
  {
    "id": 324,
    "name": "Chloe Tryon",
    "role": "Allrounder",
    "base_price": 1.0,
    "nationality": "Foreigner",
    "set": 3,
    "set_name": "WPL Foreign ARs & Bowlers (0.5-1 Cr)",
    "league": "WPL"
  },
  {
    "id": 325,
    "name": "Tara Norris",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Foreigner",
    "set": 3,
    "set_name": "WPL Foreign ARs & Bowlers (0.5-1 Cr)",
    "league": "WPL"
  },
  {
    "id": 326,
    "name": "Kathryn Bryce",
    "role": "Allrounder",
    "base_price": 1.0,
    "nationality": "Foreigner",
    "set": 3,
    "set_name": "WPL Foreign ARs & Bowlers (0.5-1 Cr)",
    "league": "WPL"
  },
  {
    "id": 327,
    "name": "Kim Garth",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Foreigner",
    "set": 3,
    "set_name": "WPL Foreign ARs & Bowlers (0.5-1 Cr)",
    "league": "WPL"
  },
  {
    "id": 328,
    "name": "Orla Prendergast",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 3,
    "set_name": "WPL Foreign ARs & Bowlers (0.5-1 Cr)",
    "league": "WPL"
  },
  {
    "id": 329,
    "name": "Kirstie Gordon",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 3,
    "set_name": "WPL Foreign ARs & Bowlers (0.5-1 Cr)",
    "league": "WPL"
  },
  {
    "id": 330,
    "name": "Lucy Hamilton",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Foreigner",
    "set": 3,
    "set_name": "WPL Foreign ARs & Bowlers (0.5-1 Cr)",
    "league": "WPL"
  },
  {
    "id": 331,
    "name": "Shafali Verma",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 4,
    "set_name": "WPL Indian Marquee (2 Cr)",
    "league": "WPL"
  },
  {
    "id": 332,
    "name": "Deepti Sharma",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 4,
    "set_name": "WPL Indian Marquee (2 Cr)",
    "league": "WPL"
  },
  {
    "id": 333,
    "name": "Jemimah Rodrigues",
    "role": "Batter",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 4,
    "set_name": "WPL Indian Marquee (2 Cr)",
    "league": "WPL"
  },
  {
    "id": 334,
    "name": "Smriti Mandhana",
    "role": "Batter",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 4,
    "set_name": "WPL Indian Marquee (2 Cr)",
    "league": "WPL"
  },
  {
    "id": 335,
    "name": "Harmanpreet Kaur",
    "role": "Batter",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 4,
    "set_name": "WPL Indian Marquee (2 Cr)",
    "league": "WPL"
  },
  {
    "id": 336,
    "name": "Richa Ghosh",
    "role": "Wicketkeeper",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 4,
    "set_name": "WPL Indian Marquee (2 Cr)",
    "league": "WPL"
  },
  {
    "id": 337,
    "name": "Amanjot Kaur",
    "role": "Allrounder",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 4,
    "set_name": "WPL Indian Marquee (2 Cr)",
    "league": "WPL"
  },
  {
    "id": 338,
    "name": "Harleen Deol",
    "role": "Batter",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 4,
    "set_name": "WPL Indian Marquee (2 Cr)",
    "league": "WPL"
  },
  {
    "id": 339,
    "name": "Bharati Fulmali",
    "role": "Batter",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 4,
    "set_name": "WPL Indian Marquee (2 Cr)",
    "league": "WPL"
  },
  {
    "id": 340,
    "name": "Sree Charani",
    "role": "Bowler",
    "base_price": 2.0,
    "nationality": "Indian",
    "set": 4,
    "set_name": "WPL Indian Marquee (2 Cr)",
    "league": "WPL"
  },
  {
    "id": 341,
    "name": "Radha Yadav",
    "role": "Allrounder",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 5,
    "set_name": "WPL Indian Stars (1 Cr)",
    "league": "WPL"
  },
  {
    "id": 342,
    "name": "Shreyanka Patil",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 5,
    "set_name": "WPL Indian Stars (1 Cr)",
    "league": "WPL"
  },
  {
    "id": 343,
    "name": "Sayali Satghare",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 5,
    "set_name": "WPL Indian Stars (1 Cr)",
    "league": "WPL"
  },
  {
    "id": 344,
    "name": "Kiran Navgire",
    "role": "Batter",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 5,
    "set_name": "WPL Indian Stars (1 Cr)",
    "league": "WPL"
  },
  {
    "id": 345,
    "name": "Kranti Goud",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 5,
    "set_name": "WPL Indian Stars (1 Cr)",
    "league": "WPL"
  },
  {
    "id": 346,
    "name": "Shikha Pandey",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 5,
    "set_name": "WPL Indian Stars (1 Cr)",
    "league": "WPL"
  },
  {
    "id": 347,
    "name": "Asha Sobhana",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 5,
    "set_name": "WPL Indian Stars (1 Cr)",
    "league": "WPL"
  },
  {
    "id": 348,
    "name": "Yastika Bhatia",
    "role": "Wicketkeeper",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 5,
    "set_name": "WPL Indian Stars (1 Cr)",
    "league": "WPL"
  },
  {
    "id": 349,
    "name": "Renuka Singh Thakur",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 5,
    "set_name": "WPL Indian Stars (1 Cr)",
    "league": "WPL"
  },
  {
    "id": 350,
    "name": "Kashvee Gautam",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 5,
    "set_name": "WPL Indian Stars (1 Cr)",
    "league": "WPL"
  },
  {
    "id": 351,
    "name": "Sneh Rana",
    "role": "Allrounder",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 5,
    "set_name": "WPL Indian Stars (1 Cr)",
    "league": "WPL"
  },
  {
    "id": 352,
    "name": "Pooja Vastrakar",
    "role": "Allrounder",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 5,
    "set_name": "WPL Indian Stars (1 Cr)",
    "league": "WPL"
  },
  {
    "id": 353,
    "name": "Sajeevan Sajana",
    "role": "Batter",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 5,
    "set_name": "WPL Indian Stars (1 Cr)",
    "league": "WPL"
  },
  {
    "id": 354,
    "name": "Arundhati Reddy",
    "role": "Bowler",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 5,
    "set_name": "WPL Indian Stars (1 Cr)",
    "league": "WPL"
  },
  {
    "id": 355,
    "name": "Pratika Rawal",
    "role": "Batter",
    "base_price": 1.0,
    "nationality": "Indian",
    "set": 5,
    "set_name": "WPL Indian Stars (1 Cr)",
    "league": "WPL"
  },
  {
    "id": 356,
    "name": "Minnu Mani",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 6,
    "set_name": "WPL Indian Domestic Set A (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 357,
    "name": "Nandni Sharma",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 6,
    "set_name": "WPL Indian Domestic Set A (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 358,
    "name": "Kanika Ahuja",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 6,
    "set_name": "WPL Indian Domestic Set A (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 359,
    "name": "Prema Rawat",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 6,
    "set_name": "WPL Indian Domestic Set A (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 360,
    "name": "Vrinda Dinesh",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 6,
    "set_name": "WPL Indian Domestic Set A (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 361,
    "name": "Disha Kasat",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 6,
    "set_name": "WPL Indian Domestic Set A (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 362,
    "name": "Shweta Sehrawat",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 6,
    "set_name": "WPL Indian Domestic Set A (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 363,
    "name": "Sanskriti Gupta",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 6,
    "set_name": "WPL Indian Domestic Set A (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 364,
    "name": "Vaishnavi Sharma",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 6,
    "set_name": "WPL Indian Domestic Set A (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 365,
    "name": "G. Kamalini",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 6,
    "set_name": "WPL Indian Domestic Set A (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 366,
    "name": "Tanuja Kanwar",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 6,
    "set_name": "WPL Indian Domestic Set A (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 367,
    "name": "Anushka Sharma",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 6,
    "set_name": "WPL Indian Domestic Set A (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 368,
    "name": "Rajeshwari Gayakwad",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 6,
    "set_name": "WPL Indian Domestic Set A (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 369,
    "name": "Niki Prasad",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 6,
    "set_name": "WPL Indian Domestic Set A (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 370,
    "name": "Uma Chetry",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 7,
    "set_name": "WPL Indian Domestic Set B (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 371,
    "name": "Nazma Khan",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 7,
    "set_name": "WPL Indian Domestic Set B (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 372,
    "name": "Madiwala Mamatha",
    "role": "Wicketkeeper",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 7,
    "set_name": "WPL Indian Domestic Set B (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 373,
    "name": "Deeya Yadav",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 7,
    "set_name": "WPL Indian Domestic Set B (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 374,
    "name": "Sushma Verma",
    "role": "Wicketkeeper",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 7,
    "set_name": "WPL Indian Domestic Set B (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 375,
    "name": "Manali Dakshini",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 7,
    "set_name": "WPL Indian Domestic Set B (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 376,
    "name": "Shipra Giri",
    "role": "Wicketkeeper",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 7,
    "set_name": "WPL Indian Domestic Set B (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 377,
    "name": "Sahana Pawar",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 7,
    "set_name": "WPL Indian Domestic Set B (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 378,
    "name": "Simran Shaikh",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 7,
    "set_name": "WPL Indian Domestic Set B (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 379,
    "name": "Jintimani Kalita",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 7,
    "set_name": "WPL Indian Domestic Set B (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 380,
    "name": "Happy Kumari",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 7,
    "set_name": "WPL Indian Domestic Set B (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 381,
    "name": "Samaira Raghav",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 7,
    "set_name": "WPL Indian Domestic Set B (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 382,
    "name": "Akshita Bhagat",
    "role": "Allrounder",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 7,
    "set_name": "WPL Indian Domestic Set B (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 383,
    "name": "Saanika Chalke",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 7,
    "set_name": "WPL Indian Domestic Set B (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 384,
    "name": "Rahila Firdous",
    "role": "Wicketkeeper",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 7,
    "set_name": "WPL Indian Domestic Set B (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 385,
    "name": "Latika Inamdar",
    "role": "Wicketkeeper",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 7,
    "set_name": "WPL Indian Domestic Set B (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 386,
    "name": "Bharti Rawal",
    "role": "Bowler",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 7,
    "set_name": "WPL Indian Domestic Set B (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 387,
    "name": "Tejal Hasabnis",
    "role": "Batter",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 7,
    "set_name": "WPL Indian Domestic Set B (0.5 Cr)",
    "league": "WPL"
  },
  {
    "id": 388,
    "name": "Kumar Prathyoosha",
    "role": "Wicketkeeper",
    "base_price": 0.5,
    "nationality": "Indian",
    "set": 7,
    "set_name": "WPL Indian Domestic Set B (0.5 Cr)",
    "league": "WPL"
  }
]

def unescape_md(text: str) -> str:
    return str(text).replace("\\_", "_").replace("\\*", "*").replace("\\`", "`") if text else ""

def escape_md(text: str) -> str:
    """Escapes underscores, asterisks, and backticks so Telegram Markdown v1 never breaks."""
    if not text:
        return ""
    return str(text).replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")

# ==============================================================================
# DATABASE SETUP & HELPERS (SUPABASE POSTGRESQL + SQLITE FALLBACK)
# ==============================================================================
def _pg_sql(sql: str) -> str:
    return sql.replace("?", "%s")

def _adapt_sql_and_params(sql: str, params: tuple):
    if not DATABASE_URL:
        return sql, params
    s = sql.strip()
    if s.upper().startswith("INSERT OR REPLACE INTO AUCTIONS"):
        s = _pg_sql(s).replace("INSERT OR REPLACE INTO auctions", "INSERT INTO auctions")
        s += " ON CONFLICT (auction_id) DO UPDATE SET chat_id=EXCLUDED.chat_id, league_type=EXCLUDED.league_type, auctioneer_id=EXCLUDED.auctioneer_id, purse_limit=EXCLUDED.purse_limit, max_players=EXCLUDED.max_players, min_players=EXCLUDED.min_players, max_foreign=EXCLUDED.max_foreign, status=EXCLUDED.status"
        return s, params
    if s.upper().startswith("INSERT OR REPLACE INTO AUCTION_TEAMS"):
        s = _pg_sql(s).replace("INSERT OR REPLACE INTO auction_teams", "INSERT INTO auction_teams")
        s += " ON CONFLICT (auction_id, team_name) DO UPDATE SET owner_id=EXCLUDED.owner_id, owner_name=EXCLUDED.owner_name, remaining_purse=EXCLUDED.remaining_purse"
        return s, params
    if s.upper().startswith("INSERT OR REPLACE INTO AUCTION_PURCHASES"):
        s = _pg_sql(s).replace("INSERT OR REPLACE INTO auction_purchases", "INSERT INTO auction_purchases")
        s += " ON CONFLICT (auction_id, player_id) DO UPDATE SET team_name=EXCLUDED.team_name, sold_price=EXCLUDED.sold_price"
        return s, params
    if s.upper().startswith("INSERT OR REPLACE INTO SCORERS"):
        s = _pg_sql(s).replace("INSERT OR REPLACE INTO scorers", "INSERT INTO scorers")
        s += " ON CONFLICT (user_id) DO UPDATE SET username=EXCLUDED.username"
        return s, params
    if "ON CONFLICT(player_id) DO UPDATE SET" in s:
        s = _pg_sql(s).replace("ON CONFLICT(player_id) DO UPDATE SET", "ON CONFLICT (player_id) DO UPDATE SET")
        s = s.replace("excluded.name", "EXCLUDED.name").replace("excluded.role", "EXCLUDED.role").replace("excluded.base_price", "EXCLUDED.base_price").replace("excluded.nationality", "EXCLUDED.nationality").replace("excluded.set_no", "EXCLUDED.set_no").replace("excluded.set_name", "EXCLUDED.set_name").replace("excluded.league", "EXCLUDED.league")
        return s, params
    return _pg_sql(s), params

class DBWrapper:
    def __init__(self, conn, is_pg: bool):
        self.conn = conn
        self.is_pg = is_pg

    def execute(self, sql: str, params: tuple = ()):
        cur = self.conn.cursor()
        q, p = _adapt_sql_and_params(sql, params)
        cur.execute(q, p)
        return _CursorWrapper(cur, self.is_pg)

    def cursor(self):
        return _CursorWrapper(self.conn.cursor(), self.is_pg)

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

class _CursorWrapper:
    def __init__(self, cur, is_pg: bool):
        self.cur = cur
        self.is_pg = is_pg

    def execute(self, sql: str, params: tuple = ()):
        q, p = _adapt_sql_and_params(sql, params)
        self.cur.execute(q, p)
        return self

    def fetchone(self):
        row = self.cur.fetchone()
        if row is None:
            return None
        if self.is_pg and isinstance(row, tuple) and self.cur.description:
            cols = [d[0] for d in self.cur.description]
            return dict(zip(cols, row))
        return row

    def fetchall(self):
        rows = self.cur.fetchall()
        if self.is_pg and self.cur.description:
            cols = [d[0] for d in self.cur.description]
            return [dict(zip(cols, r)) if isinstance(r, tuple) else r for r in rows]
        return rows

def _connect_raw():
    if DATABASE_URL:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        return conn, True
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn, False

def init_db():
    raw_conn, is_pg = _connect_raw()
    db = DBWrapper(raw_conn, is_pg)
    c = db.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS master_players (
            player_id INTEGER PRIMARY KEY,
            name TEXT,
            role TEXT,
            base_price REAL,
            nationality TEXT,
            set_no INTEGER,
            set_name TEXT,
            league TEXT DEFAULT 'IPL',
            points REAL DEFAULT 0.0
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS scorers (
            user_id BIGINT PRIMARY KEY,
            username TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS auctions (
            auction_id TEXT PRIMARY KEY,
            chat_id BIGINT,
            league_type TEXT,
            auctioneer_id BIGINT,
            purse_limit REAL,
            max_players INTEGER,
            min_players INTEGER,
            max_foreign INTEGER,
            status TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS auction_teams (
            auction_id TEXT,
            team_name TEXT,
            owner_id BIGINT,
            owner_name TEXT,
            remaining_purse REAL,
            playing_11 TEXT DEFAULT '[]',
            impact_players TEXT DEFAULT '[]',
            PRIMARY KEY (auction_id, team_name)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS auction_purchases (
            auction_id TEXT,
            player_id INTEGER,
            team_name TEXT,
            sold_price REAL,
            PRIMARY KEY (auction_id, player_id)
        )
    """)

    for p in EMBEDDED_PLAYERS:
        c.execute("""
            INSERT INTO master_players (player_id, name, role, base_price, nationality, set_no, set_name, league, points)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0.0)
            ON CONFLICT(player_id) DO UPDATE SET
                name=excluded.name,
                role=excluded.role,
                base_price=excluded.base_price,
                nationality=excluded.nationality,
                set_no=excluded.set_no,
                set_name=excluded.set_name,
                league=excluded.league
        """, (p["id"], p["name"], p["role"], p["base_price"], p["nationality"], p["set"], p["set_name"], p.get("league", "IPL")))
    db.commit()
    db.close()

def get_db_connection():
    raw_conn, is_pg = _connect_raw()
    return DBWrapper(raw_conn, is_pg)

# ==============================================================================
# IN-MEMORY LIVE AUCTION & SET11 SESSIONS
# ==============================================================================
class LiveAuction:
    def __init__(self, chat_id: int, league_type: str):
        self.chat_id = chat_id
        self.auction_id = f"AUC-{uuid.uuid4().hex[:6].upper()}"
        self.league_type = league_type  # 'IPL' or 'WPL'
        self.auctioneer_id: Optional[int] = None
        self.auctioneer_name: str = ""
        self.started: bool = False
        self.paused: bool = False
        self.automode: bool = False

        # Conditions (Defaults: 120 Cr, Max 25, Min 18, Max Foreign 8)
        self.purse_limit: float = 120.0
        self.max_players: int = 25
        self.min_players: int = 18
        self.max_foreign: int = 8

        # Teams & Owners: team_name -> {owner_id, owner_name, purse, squad: List[dict]}
        self.teams: Dict[str, dict] = {}
        self.available_teams = IPL_TEAMS.copy() if league_type == "IPL" else WPL_TEAMS.copy()

        self.pending_owner: Optional[Tuple[int, str]] = None
        self.pending_replace_user: Optional[Tuple[int, str]] = None

        self.current_set_no: Optional[int] = None
        self.current_queue: List[dict] = []
        self.sold_player_ids: set = set()
        self.unsold_player_ids: List[int] = []

        self.active_player: Optional[dict] = None
        self.current_bid: float = 0.0
        self.current_bidder_team: Optional[str] = None
        self.bid_history: List[Tuple[str, float, float]] = []
        self.timer_task: Optional[asyncio.Task] = None
        self.active_msg_id: Optional[int] = None

live_auctions: Dict[int, LiveAuction] = {}
set11_sessions: Dict[Tuple[int, int], dict] = {}

# ==============================================================================
# HELPER FUNCTIONS FOR CHECKS & CALCULATIONS
# ==============================================================================
async def is_group_admin_or_creator(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    if user_id == SUPER_ADMIN_ID:
        return True
    if update.effective_chat.type in ["group", "supergroup"]:
        member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
        return member.status in ["administrator", "creator"]
    return True

def get_user_team(auction: LiveAuction, user_id: int) -> Optional[str]:
    for t_name, info in auction.teams.items():
        if info["owner_id"] == user_id:
            return t_name
    return None


def find_player_master(query: str, league: Optional[str] = None) -> Optional[dict]:
    if not query:
        return None
    q = query.strip().lstrip("#")
    conn = get_db_connection()
    try:
        if q.isdigit():
            pid = int(q)
            if league:
                row = conn.execute(
                    "SELECT * FROM master_players WHERE player_id = ? AND league = ?",
                    (pid, league)
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT * FROM master_players WHERE player_id = ?",
                    (pid,)
                ).fetchone()
            return dict(row) if row else None

        like_q = f"%{q}%"
        if league:
            rows = conn.execute(
                "SELECT * FROM master_players WHERE LOWER(name) LIKE LOWER(?) AND league = ? ORDER BY player_id ASC",
                (like_q, league)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM master_players WHERE LOWER(name) LIKE LOWER(?) ORDER BY player_id ASC",
                (like_q,)
            ).fetchall()

        if not rows:
            return None
        for r in rows:
            if r["name"].lower() == q.lower():
                return dict(r)
        return dict(rows[0])
    finally:
        conn.close()

def is_scorer(user_id: int) -> bool:
    if user_id == SUPER_ADMIN_ID:
        return True
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT 1 FROM scorers WHERE user_id = ?", (user_id,)).fetchone()
        return row is not None
    finally:
        conn.close()

def calculate_effective_team_points(playing_11_ids: List[int], impact_ids: List[int]) -> Tuple[float, List[dict], List[str], set]:
    """
    Calculates points for a team's Playing 11 with automatic Impact Player substitution:
    - Max 4 foreigners in Playing 11
    - At least 1 Wicketkeeper in Playing 11
    - Impact player automatically replaces a Playing 11 player if they scored more points,
      without violating the max 4 Foreigner limit or minimum 1 Wicketkeeper rule.
    Returns: (total_points, final_xi_list, substitution_notes, active_counting_ids_set)
    """
    conn = get_db_connection()
    all_ids = playing_11_ids + impact_ids
    if not all_ids:
        conn.close()
        return 0.0, [], [], set()

    placeholders = ",".join("?" for _ in all_ids)
    rows = conn.execute(f"SELECT * FROM master_players WHERE player_id IN ({placeholders})", all_ids).fetchall()
    conn.close()
    p_map = {r["player_id"]: dict(r) for r in rows}

    xi = [p_map[pid] for pid in playing_11_ids if pid in p_map]
    impacts = [p_map[pid] for pid in impact_ids if pid in p_map]

    impacts.sort(key=lambda x: x["points"], reverse=True)
    subs_made = []

    for imp in impacts:
        xi_sorted = sorted(xi, key=lambda x: x["points"])
        for target in xi_sorted:
            if imp["points"] <= target["points"]:
                continue

            temp_xi = [p for p in xi if p["player_id"] != target["player_id"]] + [imp]
            foreign_count = sum(1 for p in temp_xi if p["nationality"].lower() == "foreigner")
            wk_count = sum(1 for p in temp_xi if p["role"].lower() == "wicketkeeper")

            if foreign_count <= 4 and wk_count >= 1:
                xi = temp_xi
                subs_made.append(f"🔄 {escape_md(imp['name'])} ({imp['points']} pts) replaced {escape_md(target['name'])} ({target['points']} pts)")
                break

    total_pts = sum(p["points"] for p in xi)
    counting_ids = {p["player_id"] for p in xi}
    return total_pts, xi, subs_made, counting_ids

# ==============================================================================
# GENERAL & ADMIN COMMANDS
# ==============================================================================
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🏏 *MOCK IPL / WPL AUCTION BOT COMMANDS* 🏏\n\n"
        "👥 *General & Owner Commands:*\n"
        "• `/help` - Check all available commands\n"
        "• `/start` - Start setup (Group Admins / Bot Creator)\n"
        "• `/view_set <n>` - View players in Set N (IPL: 1-20, WPL: 1-7)\n"
        "• `/purse` - View remaining purse & squad count for all teams\n"
        "• `/teamlist <team>` - View full squad & role breakdown of any team\n"
        "• `/myteamlist` or `/myteamlist <auction_id>` - View your squad & live points (works in Group & Bot PM)\n"
        "• `/unsold_players` - Check list of all unsold players\n"
        "• `/set11` or `/set11 <auction_id>` - Interactive buttons to select Playing 11 & Impact Players\n"
        "• `/ranking <auction_id>` - View live fantasy leaderboard with clickable team point buttons\n"
        "• `/top_players` - View top fantasy point scorers\n\n"
        "🔨 *Auctioneer Commands:*\n"
        "• `/change_auctioneer` - Transfer Auctioneer role (Reply/mention user or click button)\n"
        "• `/set_conditions <purse> <max_p> <min_p> <max_f>` - Set custom rules (Default: 120 25 18 8)\n"
        "• `/add_owner` - Reply/mention user to assign a team\n"
        "• `/remove_owner` - Remove an owner (players go to unsold)\n"
        "• `/replace_owner` - Reply/mention new user to replace an existing owner\n"
        "• `/start_auction` - Generate Unique Auction ID & start auction\n"
        "• `/start_set <n>` - Start bidding for Set N\n"
        "• `/newplayer` - Bring next player from current set\n"
        "• `/automode` - Toggle automatic next player (5s delay after sold/unsold)\n"
        "• `/skip_player` - Skip current player\n"
        "• `/bring_player <id or name>` - Bring specific player to bidding table\n"
        "• `/start_unsold_set` - Re-auction all unsold players\n"
        "• `/unsold <id or name>` - Remove player from a team & mark unsold (refunds purse)\n"
        "• `/pause_auction` & `/resume_auction` - Pause or resume live auction\n"
        "• `/end_auction` - Save final teams & auction data to database\n\n"
        "📊 *Scorer / Super Admin Commands:*\n"
        "• `/add_scorer` & `/remove_scorer` - Authorize/revoke scorer (Bot Owner only)\n"
        "• `/add_points <id/name> <pts>` - Add latest match points to player\n"
        "• `/set_points <id/name> <pts>` - Overwrite total points of player"
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if update.effective_chat.type in ["group", "supergroup"]:
        if not await is_group_admin_or_creator(update, context):
            await update.message.reply_text("❌ Only Group Admins or the Bot Creator can use /start in a group.")
            return

    if chat_id in live_auctions:
        ongoing = live_auctions[chat_id]
        await update.message.reply_text(
            f"⚠️ *An auction (`{ongoing.auction_id}`) is already in progress in this chat!*\n"
            f"A new auction cannot be started until the current Auctioneer or a Group Admin ends it using `/end_auction`.",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    welcome_text = (
        "Welcome to the mock auction bot, now you can make a team from scratch with friends\n"
        "After performance in real IPL/WPL, your team players will get points, make the best possible team "
        "with purse limits and other conditions to show your cricket knowledge to your friends.\n\n"
        "Choose one -"
    )
    keyboard = [
        [
            InlineKeyboardButton("◦ Mock IPL Auction", callback_data="setup_league_IPL"),
            InlineKeyboardButton("◦ Mock WPL Auction", callback_data="setup_league_WPL"),
        ]
    ]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard))

# ==============================================================================
# AUCTIONEER SETUP & OWNER MANAGEMENT
# ==============================================================================
def extract_target_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[Tuple[int, str]]:
    if update.message.reply_to_message:
        u = update.message.reply_to_message.from_user
        raw_name = f"@{u.username}" if u.username else u.full_name
        return u.id, escape_md(raw_name)
    if context.args:
        arg = context.args[0]
        if arg.isdigit():
            return int(arg), escape_md(f"User_{arg}")
        else:
            return abs(hash(arg)) % (10**10), escape_md(arg)
    return None

async def change_auctioneer_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    auction = live_auctions.get(chat_id)
    if not auction:
        await update.message.reply_text("❌ There is no active auction in this chat.")
        return

    is_admin = await is_group_admin_or_creator(update, context)
    if update.effective_user.id != auction.auctioneer_id and not is_admin:
        await update.message.reply_text("❌ Only the current Auctioneer or a Group Admin can change the Auctioneer.")
        return

    target = extract_target_user(update, context)
    if target:
        auction.auctioneer_id, auction.auctioneer_name = target
        await update.message.reply_text(
            f"🔨 *Auctioneer Changed!*\n*{auction.auctioneer_name}* is now the new Auctioneer for Auction `{auction.auction_id}`.",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        auction.auctioneer_id = None
        auction.auctioneer_name = ""
        btn = [[InlineKeyboardButton("🔨 Become Auctioneer", callback_data="become_auctioneer")]]
        await update.message.reply_text(
            "🔨 *The Auctioneer seat is now open!*\nClick the button below to become the new Auctioneer:",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=ParseMode.MARKDOWN
        )

async def set_conditions_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    auction = live_auctions.get(chat_id)
    if not auction or auction.auctioneer_id != update.effective_user.id:
        await update.message.reply_text("❌ Only the active Auctioneer can set conditions.")
        return

    if len(context.args) == 4:
        try:
            auction.purse_limit = float(context.args[0])
            auction.max_players = int(context.args[1])
            auction.min_players = int(context.args[2])
            auction.max_foreign = int(context.args[3])
        except ValueError:
            await update.message.reply_text("❌ Format: `/set_conditions <purse> <max_player> <min_player> <max_foreign>`", parse_mode=ParseMode.MARKDOWN)
            return
    else:
        auction.purse_limit, auction.max_players, auction.min_players, auction.max_foreign = 120.0, 25, 18, 8

    for t in auction.teams.values():
        t["purse"] = auction.purse_limit

    await update.message.reply_text(
        f"✅ *Auction Conditions Updated!*\n"
        f"💰 Purse: {auction.purse_limit} Cr\n"
        f"👥 Squad Size: Min {auction.min_players} | Max {auction.max_players}\n"
        f"✈️ Max Foreigners: {auction.max_foreign}\n"
        f"🧤 Mandatory: At least 1 Wicketkeeper in squad & Playing 11",
        parse_mode=ParseMode.MARKDOWN
    )

async def add_owner_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    auction = live_auctions.get(chat_id)
    if not auction or auction.auctioneer_id != update.effective_user.id:
        await update.message.reply_text("❌ Only the Auctioneer can add owners.")
        return

    target = extract_target_user(update, context)
    if not target:
        await update.message.reply_text("❌ Reply to a user or provide their UserID/username: `/add_owner @username`", parse_mode=ParseMode.MARKDOWN)
        return

    if not auction.available_teams:
        await update.message.reply_text("❌ All teams have already been assigned!")
        return

    auction.pending_owner = target
    buttons, row = [], []
    for t_name in auction.available_teams:
        row.append(InlineKeyboardButton(t_name, callback_data=f"assign_team_{t_name}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    await update.message.reply_text(
        f"Select a team to assign to *{target[1]}*:",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.MARKDOWN
    )

async def remove_owner_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    auction = live_auctions.get(chat_id)
    if not auction or auction.auctioneer_id != update.effective_user.id:
        await update.message.reply_text("❌ Only the Auctioneer can remove owners.")
        return
    if not auction.teams:
        await update.message.reply_text("❌ No teams added yet.")
        return

    buttons = [[InlineKeyboardButton(f"❌ {t} ({unescape_md(info['owner_name'])})", callback_data=f"rm_owner_{t}")]
               for t, info in auction.teams.items()]
    await update.message.reply_text("Select the team owner to remove (their bought players will move to Unsold):", reply_markup=InlineKeyboardMarkup(buttons))

async def replace_owner_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    auction = live_auctions.get(chat_id)
    if not auction or auction.auctioneer_id != update.effective_user.id:
        await update.message.reply_text("❌ Only the Auctioneer can replace owners.")
        return

    target = extract_target_user(update, context)
    if not target:
        await update.message.reply_text("❌ Reply to the new user or mention them: `/replace_owner @new_user`", parse_mode=ParseMode.MARKDOWN)
        return

    auction.pending_replace_user = target
    buttons = [[InlineKeyboardButton(f"🔄 {t} (Current: {unescape_md(info['owner_name'])})", callback_data=f"rep_owner_{t}")]
               for t, info in auction.teams.items()]
    await update.message.reply_text(f"Select which team *{target[1]}* will take over:", reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.MARKDOWN)

# ==============================================================================
# AUCTION FLOW COMMANDS
# ==============================================================================
async def start_auction_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    auction = live_auctions.get(chat_id)
    if not auction or auction.auctioneer_id != update.effective_user.id:
        await update.message.reply_text("❌ Only the Auctioneer can start the auction.")
        return
    if not auction.teams:
        await update.message.reply_text("❌ Add at least 1 team owner using `/add_owner` before starting.")
        return

    max_set = 20 if auction.league_type == "IPL" else 7
    auction.started = True
    await update.message.reply_text(
        f"🎉 *{auction.league_type} AUCTION STARTED!* 🎉\n"
        f"🆔 *Unique Auction ID:* `{auction.auction_id}`\n"
        f"_(Save this ID for setting Playing 11, viewing your team in PM, and checking rankings!)_\n\n"
        f"📋 *Registered Teams ({len(auction.teams)}):*\n" +
        "\n".join([f"• *{t}*: {info['owner_name']} ({info['purse']} Cr)" for t, info in auction.teams.items()]) +
        f"\n\n🔍 View sets using `/view_set <1-{max_set}>`\n"
        f"▶️ Auctioneer can begin a set with `/start_set <1-{max_set}>`",
        parse_mode=ParseMode.MARKDOWN
    )

async def view_set_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    auction = live_auctions.get(chat_id)

    if update.effective_chat.type in ["group", "supergroup"]:
        if not auction or auction.auctioneer_id != user_id:
            await update.message.reply_text("📩 Non-auctioneers can only check `/view_set <n>` in my Personal Message (DM) to avoid group spam!")
            return

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("📌 Usage: `/view_set <set_number>` (IPL: 1-20, WPL: 1-7)", parse_mode=ParseMode.MARKDOWN)
        return

    set_no = int(context.args[0])
    league = auction.league_type if auction else "IPL"
    if len(context.args) > 1 and context.args[1].upper() in ["IPL", "WPL"]:
        league = context.args[1].upper()

    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM master_players WHERE set_no = ? AND league = ? ORDER BY player_id",
        (set_no, league)
    ).fetchall()
    conn.close()

    if not rows:
        max_s = 20 if league == "IPL" else 7
        await update.message.reply_text(f"❌ No players found in {league} Set {set_no}. Available Sets: 1 to {max_s}.")
        return

    set_title = rows[0]["set_name"]
    lines = [f"✨ *{league} SET {set_no}: {set_title.upper()}* ✨", "━━━━━━━━━━━━━━━━━━━━"]
    for idx, r in enumerate(rows, 1):
        flag = "✈️" if r["nationality"].lower() == "foreigner" else "🇮🇳"
        role_icon = {"Batter": "🏏", "Bowler": "🎯", "Allrounder": "⚡", "Wicketkeeper": "🧤"}.get(r["role"], "🏏")
        lines.append(f"`#{r['player_id']:03d}` | {flag} *{escape_md(r['name'])}* ({role_icon} {r['role']}) — *{r['base_price']} Cr*")
    lines.append("━━━━━━━━━━━━━━━━━━━━")

    msg_text = "\n".join(lines)
    if len(msg_text) <= 4000:
        await update.message.reply_text(msg_text, parse_mode=ParseMode.MARKDOWN)
    else:
        chunk, curr_len = [], 0
        for line in lines:
            if curr_len + len(line) > 3800:
                await update.message.reply_text("\n".join(chunk), parse_mode=ParseMode.MARKDOWN)
                chunk, curr_len = [line], len(line)
            else:
                chunk.append(line)
                curr_len += len(line) + 1
        if chunk:
            await update.message.reply_text("\n".join(chunk), parse_mode=ParseMode.MARKDOWN)

def build_bidding_keyboard(has_bid: bool) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton("🔨 Start Bid (Base)" if not has_bid else "🔒 Base Bid Active", callback_data="bid_start"),
            InlineKeyboardButton("↩️ Undo My Bid (3s)", callback_data="bid_undo"),
        ],
        [
            InlineKeyboardButton("➕ 0.5 Cr", callback_data="bid_add_0.5"),
            InlineKeyboardButton("➕ 1.0 Cr", callback_data="bid_add_1.0"),
            InlineKeyboardButton("➕ 2.0 Cr", callback_data="bid_add_2.0"),
        ]
    ]
    return InlineKeyboardMarkup(buttons)

def format_player_caption(auction: LiveAuction, time_left: int) -> str:
    p = auction.active_player
    flag = "✈️ Foreigner" if p["nationality"].lower() == "foreigner" else "🇮🇳 India"
    status_line = (
        f"💰 *Current Bid:* {auction.current_bid:.1f} Cr ({auction.current_bidder_team})"
        if auction.current_bidder_team
        else f"🏷 *Awaiting Opening Bid at Base Price ({p['base_price']} Cr)*"
    )
    return (
        f"🔥 *LIVE {auction.league_type} AUCTION — SET {p['set_no']}* 🔥\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 *Player ID:* `#{p['player_id']}`\n"
        f"👤 *Name:* *{escape_md(p['name'])}*\n"
        f"🎭 *Role:* {p['role']}\n"
        f"🌍 *Nationality:* {flag}\n"
        f"💵 *Base Price:* {p['base_price']} Cr\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{status_line}\n"
        f"⏳ *Time Remaining:* `{time_left} seconds`"
    )

async def countdown_timer(context: ContextTypes.DEFAULT_TYPE, auction: LiveAuction):
    chat_id = auction.chat_id
    p = auction.active_player
    try:
        for remaining in range(19, -1, -1):
            await asyncio.sleep(1)
            while auction.paused:
                await asyncio.sleep(1)
            if remaining in (10, 5):
                try:
                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=auction.active_msg_id,
                        text=format_player_caption(auction, remaining),
                        reply_markup=build_bidding_keyboard(auction.current_bidder_team is not None),
                        parse_mode=ParseMode.MARKDOWN
                    )
                except Exception:
                    pass

        # Time is up -> Sold or Unsold
        if auction.current_bidder_team:
            team = auction.current_bidder_team
            price = auction.current_bid
            auction.teams[team]["purse"] = round(auction.teams[team]["purse"] - price, 2)
            bought_info = dict(p)
            bought_info["sold_price"] = price
            auction.teams[team]["squad"].append(bought_info)
            auction.sold_player_ids.add(p["player_id"])
            if p["player_id"] in auction.unsold_player_ids:
                auction.unsold_player_ids.remove(p["player_id"])

            result_caption = (
                f"🔨 *SOLD!* 🔨\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 *{escape_md(p['name'])}* (`#{p['player_id']}`)\n"
                f"🛡 *Bought By:* *{team}*\n"
                f"💰 *Final Price:* *{price:.1f} Cr*\n"
                f"🏦 *{team} Remaining Purse:* {auction.teams[team]['purse']:.1f} Cr"
            )
        else:
            if p["player_id"] not in auction.unsold_player_ids:
                auction.unsold_player_ids.append(p["player_id"])
            result_caption = (
                f"❌ *UNSOLD!* ❌\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 *{escape_md(p['name'])}* (`#{p['player_id']}`) goes unsold at base price {p['base_price']} Cr."
            )

        auction.active_player = None
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=auction.active_msg_id,
                text=result_caption,
                reply_markup=None,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception:
            await context.bot.send_message(chat_id=chat_id, text=result_caption, parse_mode=ParseMode.MARKDOWN)

        if auction.automode and auction.current_queue and not auction.paused:
            await context.bot.send_message(chat_id=chat_id, text="⚡ *AutoMode:* Next player coming in 5 seconds...", parse_mode=ParseMode.MARKDOWN)
            await asyncio.sleep(5)
            if not auction.paused and auction.active_player is None:
                await launch_next_player(context, auction, from_timer=True)

    except asyncio.CancelledError:
        pass

async def launch_next_player(context: ContextTypes.DEFAULT_TYPE, auction: LiveAuction, custom_player: Optional[dict] = None, from_timer: bool = False):
    if not from_timer and auction.timer_task and not auction.timer_task.done():
        auction.timer_task.cancel()

    if custom_player:
        p = custom_player
    else:
        while auction.current_queue and auction.current_queue[0]["player_id"] in auction.sold_player_ids:
            auction.current_queue.pop(0)
        if not auction.current_queue:
            await context.bot.send_message(chat_id=auction.chat_id, text="✅ *Set Completed!* Use `/start_set <n>` for the next set.", parse_mode=ParseMode.MARKDOWN)
            return
        p = auction.current_queue.pop(0)

    auction.active_player = p
    auction.current_bid = p["base_price"]
    auction.current_bidder_team = None
    auction.bid_history.clear()

    msg = await context.bot.send_message(
        chat_id=auction.chat_id,
        text=format_player_caption(auction, 20),
        reply_markup=build_bidding_keyboard(False),
        parse_mode=ParseMode.MARKDOWN
    )
    auction.active_msg_id = msg.message_id
    auction.timer_task = asyncio.create_task(countdown_timer(context, auction))

async def start_set_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    auction = live_auctions.get(chat_id)
    if not auction or auction.auctioneer_id != update.effective_user.id or not auction.started:
        await update.message.reply_text("❌ Only the Auctioneer can start a set after `/start_auction`.")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("📌 Usage: `/start_set <set_number>`", parse_mode=ParseMode.MARKDOWN)
        return

    set_no = int(context.args[0])
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM master_players WHERE set_no = ? AND league = ? ORDER BY player_id",
        (set_no, auction.league_type)
    ).fetchall()
    conn.close()

    queue = [dict(r) for r in rows if r["player_id"] not in auction.sold_player_ids]
    if not queue:
        await update.message.reply_text(f"❌ No available players left in {auction.league_type} Set {set_no}.")
        return

    auction.current_set_no = set_no
    auction.current_queue = queue
    await update.message.reply_text(f"🔔 *Starting {auction.league_type} Set {set_no}: {queue[0]['set_name']}* ({len(queue)} players)", parse_mode=ParseMode.MARKDOWN)
    await launch_next_player(context, auction)

async def newplayer_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    auction = live_auctions.get(chat_id)
    if not auction or auction.auctioneer_id != update.effective_user.id:
        return
    if auction.active_player is not None:
        await update.message.reply_text("⚠️ A player is currently on the bidding table! Use `/skip_player` to skip.")
        return
    await launch_next_player(context, auction)

async def automode_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    auction = live_auctions.get(chat_id)
    if not auction or auction.auctioneer_id != update.effective_user.id:
        await update.message.reply_text("❌ Only the Auctioneer can toggle AutoMode.")
        return
    auction.automode = not auction.automode
    state = "ENABLED ✅ (5s auto-advance)" if auction.automode else "DISABLED ❌ (manual `/newplayer`)"
    await update.message.reply_text(f"⚙️ *AutoMode is now {state}*", parse_mode=ParseMode.MARKDOWN)

    if auction.automode and auction.active_player is None and auction.current_queue and not auction.paused:
        await launch_next_player(context, auction)

async def skip_player_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    auction = live_auctions.get(chat_id)
    if not auction or auction.auctioneer_id != update.effective_user.id or not auction.active_player:
        return
    skipped = auction.active_player
    if auction.timer_task:
        auction.timer_task.cancel()
    if skipped["player_id"] not in auction.unsold_player_ids:
        auction.unsold_player_ids.append(skipped["player_id"])
    auction.active_player = None
    await update.message.reply_text(f"⏭ Skipped *{escape_md(skipped['name'])}* (Moved to Unsold list).", parse_mode=ParseMode.MARKDOWN)
    if auction.automode and auction.current_queue and not auction.paused:
        await launch_next_player(context, auction)

async def bring_player_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    auction = live_auctions.get(chat_id)
    if not auction or auction.auctioneer_id != update.effective_user.id:
        return
    if not context.args:
        await update.message.reply_text("📌 Usage: `/bring_player <player_id or name>`", parse_mode=ParseMode.MARKDOWN)
        return

    query = " ".join(context.args)
    p = find_player_master(query, league=auction.league_type)
    if not p:
        p = find_player_master(query)
    if not p:
        await update.message.reply_text("❌ Player not found.")
        return
    if p["player_id"] in auction.sold_player_ids:
        await update.message.reply_text(f"❌ *{escape_md(p['name'])}* is already sold!", parse_mode=ParseMode.MARKDOWN)
        return

    auction.current_queue = [x for x in auction.current_queue if x["player_id"] != p["player_id"]]
    await launch_next_player(context, auction, custom_player=p)

async def unsold_players_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    auction = live_auctions.get(chat_id)
    if not auction or not auction.unsold_player_ids:
        await update.message.reply_text("📭 No unsold players yet.")
        return

    conn = get_db_connection()
    placeholders = ",".join("?" for _ in auction.unsold_player_ids)
    rows = conn.execute(f"SELECT * FROM master_players WHERE player_id IN ({placeholders})", auction.unsold_player_ids).fetchall()
    conn.close()

    lines = [f"📋 *UNSOLD PLAYERS LIST ({len(rows)})* 📋", "━━━━━━━━━━━━━━━━━━━━"]
    for r in rows:
        lines.append(f"• `#{r['player_id']}` *{escape_md(r['name'])}* ({r['role']}) — Base: {r['base_price']} Cr")

    chunk, curr_len = [], 0
    for line in lines:
        if curr_len + len(line) > 3800:
            await update.message.reply_text("\n".join(chunk), parse_mode=ParseMode.MARKDOWN)
            chunk, curr_len = [line], len(line)
        else:
            chunk.append(line)
            curr_len += len(line) + 1
    if chunk:
        await update.message.reply_text("\n".join(chunk), parse_mode=ParseMode.MARKDOWN)

async def start_unsold_set_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    auction = live_auctions.get(chat_id)
    if not auction or auction.auctioneer_id != update.effective_user.id:
        return
    if not auction.unsold_player_ids:
        await update.message.reply_text("❌ No players in the Unsold list to re-auction.")
        return

    conn = get_db_connection()
    placeholders = ",".join("?" for _ in auction.unsold_player_ids)
    rows = conn.execute(f"SELECT * FROM master_players WHERE player_id IN ({placeholders})", auction.unsold_player_ids).fetchall()
    conn.close()

    auction.current_queue = [dict(r) for r in rows]
    auction.unsold_player_ids.clear()
    await update.message.reply_text(f"♻️ *Starting Re-Auction of Unsold Set ({len(auction.current_queue)} players)!*", parse_mode=ParseMode.MARKDOWN)
    await launch_next_player(context, auction)

async def unsold_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    auction = live_auctions.get(chat_id)
    if not auction or auction.auctioneer_id != update.effective_user.id:
        return
    if not context.args:
        await update.message.reply_text("📌 Usage: `/unsold <player_id or name>`", parse_mode=ParseMode.MARKDOWN)
        return

    p = find_player_master(" ".join(context.args), league=auction.league_type) or find_player_master(" ".join(context.args))
    if not p:
        await update.message.reply_text("❌ Player not found.")
        return

    pid = p["player_id"]
    removed_from = None
    refund = 0.0
    for t_name, info in auction.teams.items():
        for bought in info["squad"]:
            if bought["player_id"] == pid:
                refund = bought["sold_price"]
                info["squad"].remove(bought)
                info["purse"] = round(info["purse"] + refund, 2)
                removed_from = t_name
                break

    auction.sold_player_ids.discard(pid)
    if pid not in auction.unsold_player_ids:
        auction.unsold_player_ids.append(pid)

    if removed_from:
        await update.message.reply_text(
            f"♻️ *{escape_md(p['name'])}* removed from *{removed_from}* (Refunded {refund:.1f} Cr) and added to Unsold list.",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text(f"♻️ *{escape_md(p['name'])}* marked as Unsold.", parse_mode=ParseMode.MARKDOWN)

async def pause_auction_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    auction = live_auctions.get(update.effective_chat.id)
    if auction and auction.auctioneer_id == update.effective_user.id:
        auction.paused = True
        await update.message.reply_text("⏸ *Auction Paused!* Use `/resume_auction` to continue.", parse_mode=ParseMode.MARKDOWN)

async def resume_auction_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    auction = live_auctions.get(update.effective_chat.id)
    if auction and auction.auctioneer_id == update.effective_user.id:
        auction.paused = False
        await update.message.reply_text("▶️ *Auction Resumed!*", parse_mode=ParseMode.MARKDOWN)
        if auction.automode and auction.active_player is None and auction.current_queue:
            await launch_next_player(context, auction)

async def end_auction_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    auction = live_auctions.get(chat_id)
    if not auction:
        await update.message.reply_text("❌ There is no ongoing auction in this chat.")
        return

    is_admin = await is_group_admin_or_creator(update, context)
    if update.effective_user.id != auction.auctioneer_id and not is_admin:
        await update.message.reply_text("❌ Only the Auctioneer or a Group Admin can end the auction using `/end_auction`.", parse_mode=ParseMode.MARKDOWN)
        return

    if auction.timer_task:
        auction.timer_task.cancel()

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO auctions
        (auction_id, chat_id, league_type, auctioneer_id, purse_limit, max_players, min_players, max_foreign, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'COMPLETED')
    """, (auction.auction_id, chat_id, auction.league_type, auction.auctioneer_id,
          auction.purse_limit, auction.max_players, auction.min_players, auction.max_foreign))

    for t_name, info in auction.teams.items():
        c.execute("""
            INSERT OR REPLACE INTO auction_teams (auction_id, team_name, owner_id, owner_name, remaining_purse)
            VALUES (?, ?, ?, ?, ?)
        """, (auction.auction_id, t_name, info["owner_id"], info["owner_name"], info["purse"]))
        for sp in info["squad"]:
            c.execute("""
                INSERT OR REPLACE INTO auction_purchases (auction_id, player_id, team_name, sold_price)
                VALUES (?, ?, ?, ?)
            """, (auction.auction_id, sp["player_id"], t_name, sp["sold_price"]))

    conn.commit()
    conn.close()

    live_auctions.pop(chat_id, None)

    await update.message.reply_text(
        f"🏁 *AUCTION ENDED & SAVED!* 🏁\n"
        f"🆔 *Auction ID:* `{auction.auction_id}`\n\n"
        f"👉 All team owners can now select their Playing 11 & Impact Players interactively using:\n"
        f"`/set11 {auction.auction_id}` (or simply `/set11`)\n\n"
        f"📋 Check your saved team & live points anytime in PM with `/myteamlist {auction.auction_id}`\n"
        f"🏆 Check live rankings anytime with `/ranking {auction.auction_id}`",
        parse_mode=ParseMode.MARKDOWN
    )

# ==============================================================================
# TEAM & PURSE INSPECTION COMMANDS (LIVE + HISTORICAL SAVED AUCTIONS)
# ==============================================================================
async def purse_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    auction = live_auctions.get(update.effective_chat.id)
    if not auction or not auction.teams:
        await update.message.reply_text("❌ No active auction teams in this chat.")
        return

    lines = ["💰 *Purse details for all teams:*", ""]
    for t_name, info in auction.teams.items():
        lines.append(f"*{t_name}* - {info['purse']:.1f} cr left (squad {len(info['squad'])}/{auction.max_players})")
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)

def format_live_team_details(auction: LiveAuction, team_key: str) -> str:
    info = auction.teams[team_key]
    squad = info["squad"]
    foreign_cnt = sum(1 for p in squad if p["nationality"].lower() == "foreigner")
    bat_cnt = sum(1 for p in squad if p["role"].lower() == "batter")
    bowl_cnt = sum(1 for p in squad if p["role"].lower() == "bowler")
    ar_cnt = sum(1 for p in squad if p["role"].lower() == "allrounder")
    wk_cnt = sum(1 for p in squad if p["role"].lower() == "wicketkeeper")

    # Fetch latest points from DB for live display
    conn = get_db_connection()
    pts_map = {}
    if squad:
        pids = [p["player_id"] for p in squad]
        ph = ",".join("?" for _ in pids)
        for r in conn.execute(f"SELECT player_id, points FROM master_players WHERE player_id IN ({ph})", pids).fetchall():
            pts_map[r["player_id"]] = r["points"]
    conn.close()

    header = (
        f"🛡 *TEAM: {team_key}* (`{auction.auction_id}`)\n"
        f"💰 Remaining Purse: {info['purse']:.1f} Cr\n"
        f"👥 Total Squad: {len(squad)} / {auction.max_players} (Min: {auction.min_players})\n"
        f"✈️ Foreigners: {foreign_cnt} / {auction.max_foreign}\n"
        f"📊 Roles: Bat: {bat_cnt} | Bowl: {bowl_cnt} | AR: {ar_cnt} | WK: {wk_cnt}\n\n"
        f"*Bought Players:*\n"
    )
    if not squad:
        return header + "_No players bought yet._"

    p_lines = []
    for idx, p in enumerate(squad, 1):
        fl = " ✈️" if p["nationality"].lower() == "foreigner" else ""
        pts = pts_map.get(p["player_id"], 0.0)
        p_lines.append(f"{idx}. {escape_md(p['name'])}{fl} ({p['role']}) - {p['sold_price']:.1f} Cr | *{pts:.1f} Pts*")
    return header + "\n".join(p_lines)

def format_saved_team_details(auction_id: str, team_name: str) -> Optional[str]:
    conn = get_db_connection()
    auc_row = conn.execute("SELECT * FROM auctions WHERE auction_id = ?", (auction_id,)).fetchone()
    team_row = conn.execute(
        "SELECT * FROM auction_teams WHERE auction_id = ? AND UPPER(team_name) = ?",
        (auction_id, team_name.upper())
    ).fetchone()

    if not auc_row or not team_row:
        conn.close()
        return None

    actual_team_name = team_row["team_name"]
    rows = conn.execute("""
        SELECT m.*, ap.sold_price
        FROM auction_purchases ap
        JOIN master_players m ON ap.player_id = m.player_id
        WHERE ap.auction_id = ? AND ap.team_name = ?
        ORDER BY m.player_id ASC
    """, (auction_id, actual_team_name)).fetchall()
    conn.close()

    squad = [dict(r) for r in rows]
    foreign_cnt = sum(1 for p in squad if p["nationality"].lower() == "foreigner")
    bat_cnt = sum(1 for p in squad if p["role"].lower() == "batter")
    bowl_cnt = sum(1 for p in squad if p["role"].lower() == "bowler")
    ar_cnt = sum(1 for p in squad if p["role"].lower() == "allrounder")
    wk_cnt = sum(1 for p in squad if p["role"].lower() == "wicketkeeper")

    xi_ids = json.loads(team_row["playing_11"] or "[]")
    imp_ids = json.loads(team_row["impact_players"] or "[]")
    eff_pts, _, subs_made, counting_ids = calculate_effective_team_points(xi_ids, imp_ids)

    header = (
        f"🛡 *TEAM: {actual_team_name}* (`{auction_id}` - {auc_row['league_type']})\n"
        f"👤 Owner: {team_row['owner_name']}\n"
        f"💰 Remaining Purse: {team_row['remaining_purse']:.1f} Cr\n"
        f"👥 Total Squad: {len(squad)} / {auc_row['max_players']} (Min: {auc_row['min_players']})\n"
        f"✈️ Foreigners: {foreign_cnt} / {auc_row['max_foreign']}\n"
        f"📊 Roles: Bat: {bat_cnt} | Bowl: {bowl_cnt} | AR: {ar_cnt} | WK: {wk_cnt}\n"
        f"🏆 *Effective Fantasy Points (XI + Impact): {eff_pts:.1f} Pts*\n\n"
        f"*Squad & Live Points:*\n"
    )
    if not squad:
        return header + "_No players bought in this auction._"

    p_lines = []
    for idx, p in enumerate(squad, 1):
        fl = " ✈️" if p["nationality"].lower() == "foreigner" else ""
        pid = p["player_id"]
        tag = ""
        if pid in counting_ids:
            tag = " [XI✅]"
        elif pid in imp_ids:
            tag = " [IMP]"
        elif pid in xi_ids:
            tag = " [XI-Subbed]"
        p_lines.append(
            f"{idx}. *{escape_md(p['name'])}*{fl} ({p['role']}) — {p['sold_price']:.1f} Cr | *{p['points']:.1f} Pts*{tag}"
        )

    footer = ""
    if subs_made:
        footer = "\n\n⚡ *Active Impact Substitutions:*\n" + "\n".join([f"• _{s}_" for s in subs_made])

    return header + "\n".join(p_lines) + footer

async def teamlist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    auction = live_auctions.get(chat_id)

    if not context.args:
        await update.message.reply_text(
            "📌 Usage:\n• In active group: `/teamlist <team_name>`\n• For saved auction: `/teamlist <team_name> <auction_id>`",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    target_team = context.args[0].upper()

    # If auction_id is explicitly provided as 2nd argument
    if len(context.args) >= 2:
        auction_id = context.args[1].upper()
        saved_text = format_saved_team_details(auction_id, target_team)
        if not saved_text:
            await update.message.reply_text(f"❌ Team `{target_team}` not found in Auction `{auction_id}`.", parse_mode=ParseMode.MARKDOWN)
            return
        await update.message.reply_text(saved_text, parse_mode=ParseMode.MARKDOWN)
        return

    if auction:
        matched = next((t for t in auction.teams if t.upper() == target_team), None)
        if not matched:
            await update.message.reply_text(f"❌ Team `{target_team}` not found in current auction.", parse_mode=ParseMode.MARKDOWN)
            return
        await update.message.reply_text(format_live_team_details(auction, matched), parse_mode=ParseMode.MARKDOWN)
        return

    await update.message.reply_text("📌 No live auction in this chat. Use `/teamlist <team_name> <auction_id>` for past auctions.", parse_mode=ParseMode.MARKDOWN)

async def myteamlist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # 1. If <auction_id> is provided (works in Bot PM as well as any group!)
    if context.args:
        auction_id = context.args[0].upper()

        # Check if that auction_id is currently live in any group
        live_match = next((a for a in live_auctions.values() if a.auction_id == auction_id), None)
        if live_match:
            t_name = get_user_team(live_match, user_id)
            if not t_name:
                await update.message.reply_text(f"❌ You do not own a team in live Auction `{auction_id}`.", parse_mode=ParseMode.MARKDOWN)
                return
            await update.message.reply_text(format_live_team_details(live_match, t_name), parse_mode=ParseMode.MARKDOWN)
            return

        # Otherwise fetch from saved auctions in SQLite DB
        conn = get_db_connection()
        team_row = conn.execute(
            "SELECT team_name FROM auction_teams WHERE auction_id = ? AND owner_id = ?",
            (auction_id, user_id)
        ).fetchone()
        conn.close()

        if not team_row:
            await update.message.reply_text(
                f"❌ You do not have a saved team in Auction `{auction_id}` (or the Auction ID is invalid).",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        saved_text = format_saved_team_details(auction_id, team_row["team_name"])
        await update.message.reply_text(saved_text, parse_mode=ParseMode.MARKDOWN)
        return

    # 2. If no argument given in a group with a live auction -> show live team
    auction = live_auctions.get(chat_id)
    if auction:
        t_name = get_user_team(auction, user_id)
        if not t_name:
            await update.message.reply_text("❌ You do not own a team in this auction.")
            return
        await update.message.reply_text(format_live_team_details(auction, t_name), parse_mode=ParseMode.MARKDOWN)
        return

    # 3. If no argument given in Bot PM (or chat without live auction) -> list user's saved auctions or show latest
    conn = get_db_connection()
    user_auctions = conn.execute("""
        SELECT at.auction_id, at.team_name, a.league_type
        FROM auction_teams at
        JOIN auctions a ON at.auction_id = a.auction_id
        WHERE at.owner_id = ?
        ORDER BY a.auction_id DESC
    """, (user_id,)).fetchall()
    conn.close()

    if not user_auctions:
        await update.message.reply_text("❌ You haven't participated in any saved auctions yet. Use `/myteamlist <auction_id>`.")
        return

    if len(user_auctions) == 1:
        only = user_auctions[0]
        await update.message.reply_text(format_saved_team_details(only["auction_id"], only["team_name"]), parse_mode=ParseMode.MARKDOWN)
    else:
        lines = [
            "📋 *Your Past & Completed Auctions:*",
            "Send `/myteamlist <auction_id>` to view full squad & updated points for any auction:\n"
        ]
        for ua in user_auctions:
            lines.append(f"• `{ua['auction_id']}` — *{ua['team_name']}* ({ua['league_type']})")
        await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)

# ==============================================================================
# INTERACTIVE /SET11 BUILDER & RANKING COMMANDS
# ==============================================================================
def render_set11_Menu(session: dict) -> Tuple[str, InlineKeyboardMarkup]:
    stage = session["stage"]
    squad = session["squad"]
    xi_ids = session["xi_ids"]
    imp_ids = session["impact_ids"]
    p_map = {p["player_id"]: p for p in squad}

    xi_players = [p_map[pid] for pid in xi_ids]
    f_cnt = sum(1 for p in xi_players if p["nationality"].lower() == "foreigner")
    wk_cnt = sum(1 for p in xi_players if p["role"].lower() == "wicketkeeper")

    role_short = {"Batter": "Bat", "Bowler": "Bowl", "Allrounder": "AR", "Wicketkeeper": "WK"}

    if stage == "XI":
        text = (
            f"🏏 *SELECT PLAYING 11 — {session['team_name']} (`{session['auction_id']}`)*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ *Selected:* `{len(xi_ids)} / 11`\n"
            f"✈️ *Foreigners:* `{f_cnt} / 4`  |  🧤 *Wicketkeepers:* `{wk_cnt}` (Min 1)\n\n"
            f"👇 _Tap player buttons below to select or deselect your main 11 players:_"
        )
        buttons, row = [], []
        for p in squad:
            pid = p["player_id"]
            is_sel = pid in xi_ids
            mark = "✅ " if is_sel else ""
            fl = "✈️" if p["nationality"].lower() == "foreigner" else ""
            r_tag = role_short.get(p["role"], p["role"])
            btn_label = f"{mark}{p['name']}{fl} ({r_tag})"
            row.append(InlineKeyboardButton(btn_label, callback_data=f"s11_xi_{pid}"))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)

        if len(xi_ids) == 11:
            buttons.append([InlineKeyboardButton("➡️ Next: Choose Impact Players (Optional)", callback_data="s11_to_imp")])
            buttons.append([InlineKeyboardButton("💾 Submit Playing 11 (Without Impact)", callback_data="s11_submit")])
        return text, InlineKeyboardMarkup(buttons)

    else:
        text = (
            f"⚡ *SELECT IMPACT PLAYERS (OPTIONAL) — {session['team_name']}*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ *Playing 11 Locked:* 11 Players (✈️ {f_cnt}/4 | 🧤 WK: {wk_cnt})\n"
            f"🔄 *Impact Players Selected:* `{len(imp_ids)} / 4` (Optional)\n\n"
            f"👇 _Tap up to 4 bench players as Impact Players, or click Submit directly:_"
        )
        buttons, row = [], []
        bench = [p for p in squad if p["player_id"] not in xi_ids]
        for p in bench:
            pid = p["player_id"]
            is_sel = pid in imp_ids
            mark = "⭐ " if is_sel else ""
            fl = "✈️" if p["nationality"].lower() == "foreigner" else ""
            r_tag = role_short.get(p["role"], p["role"])
            btn_label = f"{mark}{p['name']}{fl} ({r_tag})"
            row.append(InlineKeyboardButton(btn_label, callback_data=f"s11_imp_{pid}"))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)

        buttons.append([
            InlineKeyboardButton("⬅️ Back to Playing 11", callback_data="s11_back_xi"),
            InlineKeyboardButton("💾 Submit Final Team", callback_data="s11_submit")
        ])
        return text, InlineKeyboardMarkup(buttons)

async def set11_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    conn = get_db_connection()
    auction_id = None

    if context.args:
        auction_id = context.args[0].upper()
    else:
        row = conn.execute(
            "SELECT auction_id FROM auction_teams WHERE owner_id = ? ORDER BY auction_id DESC LIMIT 1",
            (user_id,)
        ).fetchone()
        if row:
            auction_id = row["auction_id"]
        elif chat_id in live_auctions:
            await update.message.reply_text("⚠️ Please ask the Auctioneer to run `/end_auction` first so teams are saved before setting Playing 11.")
            conn.close()
            return

    if not auction_id:
        conn.close()
        await update.message.reply_text("📌 Usage: `/set11 <auction_id>` (e.g., `/set11 AUC-1A2B3C`)", parse_mode=ParseMode.MARKDOWN)
        return

    team_row = conn.execute(
        "SELECT * FROM auction_teams WHERE auction_id = ? AND owner_id = ?",
        (auction_id, user_id)
    ).fetchone()
    if not team_row:
        conn.close()
        await update.message.reply_text(f"❌ You do not own a team in Auction `{auction_id}`.", parse_mode=ParseMode.MARKDOWN)
        return

    team_name = team_row["team_name"]
    rows = conn.execute("""
        SELECT m.* FROM master_players m
        JOIN auction_purchases ap ON m.player_id = ap.player_id
        WHERE ap.auction_id = ? AND ap.team_name = ?
        ORDER BY m.player_id ASC
    """, (auction_id, team_name)).fetchall()
    conn.close()

    squad = [dict(r) for r in rows]
    if len(squad) < 11:
        await update.message.reply_text(
            f"❌ Your squad (*{team_name}*) only has {len(squad)} players. At least 11 players are required to set a Playing 11!",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    existing_xi = json.loads(team_row["playing_11"] or "[]")
    existing_imp = json.loads(team_row["impact_players"] or "[]")
    owned_ids = {p["player_id"] for p in squad}
    existing_xi = [pid for pid in existing_xi if pid in owned_ids]
    existing_imp = [pid for pid in existing_imp if pid in owned_ids and pid not in existing_xi]

    session = {
        "auction_id": auction_id,
        "team_name": team_name,
        "stage": "XI",
        "squad": squad,
        "xi_ids": existing_xi,
        "impact_ids": existing_imp,
    }
    set11_sessions[(chat_id, user_id)] = session

    text, markup = render_set11_Menu(session)
    await update.message.reply_text(text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)

def build_ranking_view(auction_id: str) -> Optional[Tuple[str, InlineKeyboardMarkup]]:
    conn = get_db_connection()
    auc_row = conn.execute("SELECT * FROM auctions WHERE auction_id = ?", (auction_id,)).fetchone()
    teams = conn.execute("SELECT * FROM auction_teams WHERE auction_id = ?", (auction_id,)).fetchall()
    conn.close()

    if not auc_row or not teams:
        return None

    leaderboard = []
    for t in teams:
        xi_ids = json.loads(t["playing_11"] or "[]")
        imp_ids = json.loads(t["impact_players"] or "[]")
        pts, _, subs, _ = calculate_effective_team_points(xi_ids, imp_ids)
        leaderboard.append((t["team_name"], t["owner_name"], pts, subs, len(xi_ids) == 11))

    leaderboard.sort(key=lambda x: x[2], reverse=True)
    lines = [
        f"🏆 *FANTASY STANDINGS — {auction_id} ({auc_row['league_type']})* 🏆",
        "━━━━━━━━━━━━━━━━━━━━",
        "_Tap any team button below to inspect their full squad & player points:_\n"
    ]
    buttons, row = [], []
    for rank, (t_name, o_name, pts, subs, has_xi) in enumerate(leaderboard, 1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
        xi_status = "" if has_xi else " ⚠️ _(XI not set)_"
        lines.append(f"{medal} *{t_name}* ({o_name}) — *{pts:.1f} Pts*{xi_status}")
        for s in subs:
            lines.append(f"   └ _{s}_")

        btn_text = f"{medal} {t_name} — {pts:.1f} Pts"
        row.append(InlineKeyboardButton(btn_text, callback_data=f"rk_team_{auction_id}_{t_name}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    return "\n".join(lines), InlineKeyboardMarkup(buttons)

async def ranking_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_db_connection()
    if context.args:
        auction_id = context.args[0].upper()
    else:
        row = conn.execute("SELECT auction_id FROM auctions WHERE chat_id = ? ORDER BY auction_id DESC LIMIT 1", (update.effective_chat.id,)).fetchone()
        if not row:
            conn.close()
            await update.message.reply_text("📌 Usage: `/ranking <auction_unique_id>`", parse_mode=ParseMode.MARKDOWN)
            return
        auction_id = row["auction_id"]
    conn.close()

    view = build_ranking_view(auction_id)
    if not view:
        await update.message.reply_text(f"❌ Auction `{auction_id}` not found.", parse_mode=ParseMode.MARKDOWN)
        return

    text, markup = view
    await update.message.reply_text(text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)

async def add_scorer_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != SUPER_ADMIN_ID:
        await update.message.reply_text("❌ Only the Bot Creator can add scorers.")
        return
    target = extract_target_user(update, context)
    if not target:
        await update.message.reply_text("📌 Reply to a user or pass their ID: `/add_scorer <user_id>`", parse_mode=ParseMode.MARKDOWN)
        return
    conn = get_db_connection()
    conn.execute("INSERT OR REPLACE INTO scorers (user_id, username) VALUES (?, ?)", target)
    conn.commit()
    conn.close()
    await update.message.reply_text(f"✅ *{target[1]}* is now an authorized Scorer!", parse_mode=ParseMode.MARKDOWN)

async def remove_scorer_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != SUPER_ADMIN_ID:
        await update.message.reply_text("❌ Only the Bot Creator can remove scorers.")
        return
    target = extract_target_user(update, context)
    if not target:
        await update.message.reply_text("📌 Reply to a user or pass their ID: `/remove_scorer <user_id>`", parse_mode=ParseMode.MARKDOWN)
        return
    conn = get_db_connection()
    conn.execute("DELETE FROM scorers WHERE user_id = ?", (target[0],))
    conn.commit()
    conn.close()
    await update.message.reply_text(f"🗑 Removed *{target[1]}* from scorers.", parse_mode=ParseMode.MARKDOWN)

async def add_points_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_scorer(update.effective_user.id):
        await update.message.reply_text("❌ Only authorized Scorers can update player points.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("📌 Usage: `/add_points <player_id or name> <points>`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        pts = float(context.args[-1])
    except ValueError:
        await update.message.reply_text("❌ Points must be a numeric value.")
        return

    p = find_player_master(" ".join(context.args[:-1]))
    if not p:
        await update.message.reply_text("❌ Player not found.")
        return

    new_total = p["points"] + pts
    conn = get_db_connection()
    conn.execute("UPDATE master_players SET points = ? WHERE player_id = ?", (new_total, p["player_id"]))
    conn.commit()
    conn.close()
    await update.message.reply_text(f"✅ Added *{pts:+.1f} pts* to *{escape_md(p['name'])}* (`#{p['player_id']}` - {p['league']}). Total: *{new_total:.1f} pts*", parse_mode=ParseMode.MARKDOWN)

async def set_points_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_scorer(update.effective_user.id):
        await update.message.reply_text("❌ Only authorized Scorers can set player points.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("📌 Usage: `/set_points <player_id or name> <total_points>`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        pts = float(context.args[-1])
    except ValueError:
        await update.message.reply_text("❌ Points must be a numeric value.")
        return

    p = find_player_master(" ".join(context.args[:-1]))
    if not p:
        await update.message.reply_text("❌ Player not found.")
        return

    conn = get_db_connection()
    conn.execute("UPDATE master_players SET points = ? WHERE player_id = ?", (pts, p["player_id"]))
    conn.commit()
    conn.close()
    await update.message.reply_text(f"✅ Set total points of *{escape_md(p['name'])}* (`#{p['player_id']}` - {p['league']}) to *{pts:.1f} pts*.", parse_mode=ParseMode.MARKDOWN)

def render_top_players_page(page: int) -> Tuple[str, InlineKeyboardMarkup]:
    offset = page * 10
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM master_players ORDER BY points DESC, player_id ASC LIMIT 10 OFFSET ?", (offset,)).fetchall()
    total = conn.execute("SELECT COUNT(*) FROM master_players").fetchone()[0]
    conn.close()

    lines = [f"🌟 *TOP FANTASY PLAYERS (Page {page + 1})* 🌟", "━━━━━━━━━━━━━━━━━━━━"]
    for idx, r in enumerate(rows, offset + 1):
        lines.append(f"*{idx}.* *{escape_md(r['name'])}* (`#{r['player_id']}` | {r['league']}) — *{r['points']:.1f} Pts*")

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"topp_{page - 1}"))
    if offset + 10 < total:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"topp_{page + 1}"))
    return "\n".join(lines), InlineKeyboardMarkup([nav] if nav else [])

async def top_players_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, markup = render_top_players_page(0)
    await update.message.reply_text(text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)

# ==============================================================================
# CALLBACK QUERY HANDLER (BUTTON CLICKS)
# ==============================================================================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    chat_id = query.message.chat.id
    user = query.from_user

    # 1. Ranking Team Button Click & Back Button
    if data.startswith("rk_team_"):
        # Format: rk_team_<auction_id>_<team_name>
        rest = data.replace("rk_team_", "", 1)
        auction_id, team_name = rest.split("_", 1)
        details = format_saved_team_details(auction_id, team_name)
        if not details:
            await query.answer("Team details not found.", show_alert=True)
            return
        back_kb = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Ranking", callback_data=f"rk_back_{auction_id}")]])
        await query.answer()
        await query.edit_message_text(details, reply_markup=back_kb, parse_mode=ParseMode.MARKDOWN)
        return

    if data.startswith("rk_back_"):
        auction_id = data.replace("rk_back_", "", 1)
        view = build_ranking_view(auction_id)
        if not view:
            await query.answer("Ranking not found.", show_alert=True)
            return
        text, markup = view
        await query.answer()
        await query.edit_message_text(text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)
        return

    # 2. Interactive /set11 Callbacks
    if data.startswith("s11_"):
        session = set11_sessions.get((chat_id, user.id))
        if not session:
            await query.answer("⚠️ This Playing 11 session has expired or belongs to another user. Run /set11 again.", show_alert=True)
            return

        p_map = {p["player_id"]: p for p in session["squad"]}
        xi_ids = session["xi_ids"]
        imp_ids = session["impact_ids"]

        if data.startswith("s11_xi_"):
            pid = int(data.replace("s11_xi_", ""))
            if pid in xi_ids:
                xi_ids.remove(pid)
            else:
                if len(xi_ids) >= 11:
                    await query.answer("❌ You have already selected 11 players! Deselect one first or proceed.", show_alert=True)
                    return
                cand = p_map[pid]
                curr_xi = [p_map[x] for x in xi_ids]
                f_cnt = sum(1 for x in curr_xi if x["nationality"].lower() == "foreigner")
                wk_cnt = sum(1 for x in curr_xi if x["role"].lower() == "wicketkeeper")

                if cand["nationality"].lower() == "foreigner" and f_cnt >= 4:
                    await query.answer("❌ Maximum 4 Overseas (Foreign) players are allowed in Playing 11!", show_alert=True)
                    return
                if len(xi_ids) == 10 and wk_cnt == 0 and cand["role"].lower() != "wicketkeeper":
                    await query.answer("❌ Your Playing 11 must contain at least 1 Wicketkeeper! Please select a Wicketkeeper for the 11th spot.", show_alert=True)
                    return

                xi_ids.append(pid)
                if pid in imp_ids:
                    imp_ids.remove(pid)
            await query.answer()
            text, markup = render_set11_Menu(session)
            await query.edit_message_text(text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)
            return

        if data == "s11_to_imp":
            if len(xi_ids) != 11:
                await query.answer("❌ Please select exactly 11 players first!", show_alert=True)
                return
            wk_cnt = sum(1 for x in xi_ids if p_map[x]["role"].lower() == "wicketkeeper")
            if wk_cnt < 1:
                await query.answer("❌ At least 1 Wicketkeeper is mandatory in Playing 11!", show_alert=True)
                return
            session["stage"] = "IMPACT"
            await query.answer()
            text, markup = render_set11_Menu(session)
            await query.edit_message_text(text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)
            return

        if data == "s11_back_xi":
            session["stage"] = "XI"
            await query.answer()
            text, markup = render_set11_Menu(session)
            await query.edit_message_text(text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)
            return

        if data.startswith("s11_imp_"):
            pid = int(data.replace("s11_imp_", ""))
            if pid in imp_ids:
                imp_ids.remove(pid)
            else:
                if len(imp_ids) >= 4:
                    await query.answer("❌ You can select a maximum of 4 Impact Players!", show_alert=True)
                    return
                imp_ids.append(pid)
            await query.answer()
            text, markup = render_set11_Menu(session)
            await query.edit_message_text(text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)
            return

        if data == "s11_submit":
            if len(xi_ids) != 11:
                await query.answer("❌ Please select 11 players for your Playing 11 first!", show_alert=True)
                return
            curr_xi = [p_map[x] for x in xi_ids]
            f_cnt = sum(1 for x in curr_xi if x["nationality"].lower() == "foreigner")
            wk_cnt = sum(1 for x in curr_xi if x["role"].lower() == "wicketkeeper")
            if f_cnt > 4:
                await query.answer("❌ Max 4 Foreigners allowed in Playing 11!", show_alert=True)
                return
            if wk_cnt < 1:
                await query.answer("❌ At least 1 Wicketkeeper is mandatory in Playing 11!", show_alert=True)
                return

            conn = get_db_connection()
            conn.execute(
                "UPDATE auction_teams SET playing_11 = ?, impact_players = ? WHERE auction_id = ? AND team_name = ?",
                (json.dumps(xi_ids), json.dumps(imp_ids), session["auction_id"], session["team_name"])
            )
            conn.commit()
            conn.close()

            xi_names = [f"{i}. {escape_md(p_map[pid]['name'])} ({p_map[pid]['role']})" + (" ✈️" if p_map[pid]["nationality"].lower() == "foreigner" else "")
                        for i, pid in enumerate(xi_ids, 1)]
            imp_names = [f"{i}. {escape_md(p_map[pid]['name'])} ({p_map[pid]['role']})" + (" ✈️" if p_map[pid]["nationality"].lower() == "foreigner" else "")
                         for i, pid in enumerate(imp_ids, 1)]

            summary_text = (
                f"✅ *PLAYING 11 & IMPACT PLAYERS SAVED!*\n"
                f"🛡 *Team:* *{session['team_name']}* (`{session['auction_id']}`)\n"
                f"✈️ Foreigners in XI: {f_cnt}/4 | 🧤 Wicketkeepers: {wk_cnt}\n\n"
                f"🏏 *Playing 11:*\n" + "\n".join(xi_names) + "\n\n"
                f"⚡ *Impact Players ({len(imp_ids)}/4):*\n" + ("\n".join(imp_names) if imp_names else "_None selected_")
            )
            set11_sessions.pop((chat_id, user.id), None)
            await query.answer("✅ Team Saved Successfully!")
            await query.edit_message_text(summary_text, parse_mode=ParseMode.MARKDOWN)
            return

    # 3. League Selection
    if data.startswith("setup_league_"):
        if chat_id in live_auctions:
            await query.answer("⚠️ Please end the ongoing auction using /end_auction first!", show_alert=True)
            return
        league = data.replace("setup_league_", "")
        live_auctions[chat_id] = LiveAuction(chat_id, league)
        btn = [[InlineKeyboardButton("🔨 Become Auctioneer", callback_data="become_auctioneer")]]
        await query.edit_message_text(
            f"✅ *Mock {league} Auction Selected!*\n\nClick the button below to become the Auctioneer:",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # 4. Become Auctioneer
    if data == "become_auctioneer":
        auction = live_auctions.get(chat_id)
        if not auction:
            await query.answer("No active auction setup!", show_alert=True)
            return
        if auction.auctioneer_id is not None:
            await query.answer(f"{unescape_md(auction.auctioneer_name)} is already the Auctioneer!", show_alert=True)
            return
        auction.auctioneer_id = user.id
        auction.auctioneer_name = escape_md(f"@{user.username}" if user.username else user.full_name)
        await query.edit_message_text(
            f"🔨 *{auction.auctioneer_name}* is now the *{auction.league_type} Auctioneer*!\n\n"
            f"⚙️ Current Conditions: `{auction.purse_limit} Cr | Max {auction.max_players} | Min {auction.min_players} | Max {auction.max_foreign} Foreigners | Min 1 WK`\n"
            f"• Change rules: `/set_conditions <purse> <max> <min> <foreign>`\n"
            f"• Add team owners: `/add_owner` (reply to user)\n"
            f"• Change auctioneer anytime: `/change_auctioneer`\n"
            f"• Start auction: `/start_auction`",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # 5. Pagination for Top Players
    if data.startswith("topp_"):
        page = int(data.replace("topp_", ""))
        text, markup = render_top_players_page(page)
        await query.edit_message_text(text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)
        return

    auction = live_auctions.get(chat_id)
    if not auction:
        await query.answer("No active auction in this chat.", show_alert=True)
        return

    # 6. Owner Assignment / Removal / Replacement (Auctioneer Only)
    if data.startswith(("assign_team_", "rm_owner_", "rep_owner_")):
        if user.id != auction.auctioneer_id:
            await query.answer("Only the Auctioneer can manage team owners!", show_alert=True)
            return

        if data.startswith("assign_team_"):
            t_name = data.replace("assign_team_", "")
            if not auction.pending_owner or t_name not in auction.available_teams:
                await query.answer("Team unavailable or request expired.", show_alert=True)
                return
            u_id, u_name = auction.pending_owner
            auction.available_teams.remove(t_name)
            auction.teams[t_name] = {"owner_id": u_id, "owner_name": u_name, "purse": auction.purse_limit, "squad": []}
            auction.pending_owner = None
            await query.edit_message_text(f"✅ Assigned *{t_name}* to *{u_name}* (Purse: {auction.purse_limit} Cr)!", parse_mode=ParseMode.MARKDOWN)

        elif data.startswith("rm_owner_"):
            t_name = data.replace("rm_owner_", "")
            info = auction.teams.pop(t_name, None)
            if info:
                auction.available_teams.append(t_name)
                for p in info["squad"]:
                    auction.sold_player_ids.discard(p["player_id"])
                    if p["player_id"] not in auction.unsold_player_ids:
                        auction.unsold_player_ids.append(p["player_id"])
                await query.edit_message_text(f"🗑 Removed *{t_name}* ({info['owner_name']}). Their {len(info['squad'])} bought players moved to Unsold list.", parse_mode=ParseMode.MARKDOWN)

        elif data.startswith("rep_owner_"):
            t_name = data.replace("rep_owner_", "")
            if t_name in auction.teams and auction.pending_replace_user:
                old_name = auction.teams[t_name]["owner_name"]
                u_id, u_name = auction.pending_replace_user
                auction.teams[t_name]["owner_id"] = u_id
                auction.teams[t_name]["owner_name"] = u_name
                auction.pending_replace_user = None
                await query.edit_message_text(f"🔄 Replaced *{old_name}* with *{u_name}* as owner of *{t_name}*!", parse_mode=ParseMode.MARKDOWN)
        return

    # 7. Live Bidding Buttons
    if data.startswith("bid_"):
        if auction.paused:
            await query.answer("⏸ Auction is currently paused!", show_alert=True)
            return
        p = auction.active_player
        if not p:
            await query.answer("No active player on the bidding table!", show_alert=True)
            return

        team_name = get_user_team(auction, user.id)
        if not team_name:
            await query.answer("❌ Only registered Team Owners can bid!", show_alert=True)
            return

        t_info = auction.teams[team_name]

        # Undo Bid (Valid within 3 seconds of placing the top bid)
        if data == "bid_undo":
            if auction.current_bidder_team != team_name or not auction.bid_history:
                await query.answer("You do not hold the current highest bid!", show_alert=True)
                return
            last_team, last_amt, last_ts = auction.bid_history[-1]
            if time.time() - last_ts > 3.0:
                await query.answer("⏳ Undo window (3 seconds) has expired!", show_alert=True)
                return

            auction.bid_history.pop()
            if auction.bid_history:
                prev_team, prev_amt, _ = auction.bid_history[-1]
                auction.current_bidder_team = prev_team
                auction.current_bid = prev_amt
            else:
                auction.current_bidder_team = None
                auction.current_bid = p["base_price"]

            if auction.timer_task:
                auction.timer_task.cancel()
            auction.timer_task = asyncio.create_task(countdown_timer(context, auction))
            await query.answer("↩️ Bid undone! Timer reset to 20s.")
            await query.edit_message_text(
                text=format_player_caption(auction, 20),
                reply_markup=build_bidding_keyboard(auction.current_bidder_team is not None),
                parse_mode=ParseMode.MARKDOWN
            )
            return

        # Place / Increment Bid
        if data == "bid_start":
            if auction.current_bidder_team is not None:
                await query.answer("Opening bid already placed! Use +0.5, +1.0, or +2.0 Cr.", show_alert=True)
                return
            new_bid = p["base_price"]
        else:
            inc = float(data.replace("bid_add_", ""))
            if auction.current_bidder_team is None:
                new_bid = round(p["base_price"] + inc, 2)
            else:
                if auction.current_bidder_team == team_name:
                    await query.answer("You already hold the highest bid!", show_alert=True)
                    return
                new_bid = round(auction.current_bid + inc, 2)

        # Validate Squad Limit, Purse, Mandatory Minimum Purse Reserve, Foreigner Limit, and Mandatory Wicketkeeper Slot
        current_squad_size = len(t_info["squad"])
        if current_squad_size >= auction.max_players:
            await query.answer(f"❌ Squad full ({auction.max_players}/{auction.max_players})!", show_alert=True)
            return

        if new_bid > t_info["purse"]:
            await query.answer(f"❌ Insufficient purse! You have {t_info['purse']:.1f} Cr.", show_alert=True)
            return

        remaining_mandatory_after_this = max(0, auction.min_players - (current_squad_size + 1))
        required_reserve = round(remaining_mandatory_after_this * 0.5, 2)
        max_allowed_bid = round(t_info["purse"] - required_reserve, 2)
        if new_bid > max_allowed_bid:
            await query.answer(
                f"❌ Max bid allowed is {max_allowed_bid:.1f} Cr! You must reserve {required_reserve:.1f} Cr (0.5 Cr × {remaining_mandatory_after_this}) to fill your minimum squad of {auction.min_players}.",
                show_alert=True
            )
            return

        if p["nationality"].lower() == "foreigner":
            f_cnt = sum(1 for x in t_info["squad"] if x["nationality"].lower() == "foreigner")
            if f_cnt >= auction.max_foreign:
                await query.answer(f"❌ Max Foreigner limit ({auction.max_foreign}) reached!", show_alert=True)
                return

        has_wk = any(x["role"].lower() == "wicketkeeper" for x in t_info["squad"])
        if not has_wk and current_squad_size == auction.max_players - 1 and p["role"].lower() != "wicketkeeper":
            await query.answer("❌ Your last squad slot is reserved for a mandatory Wicketkeeper!", show_alert=True)
            return

        auction.current_bid = new_bid
        auction.current_bidder_team = team_name
        auction.bid_history.append((team_name, new_bid, time.time()))

        if auction.timer_task:
            auction.timer_task.cancel()
        auction.timer_task = asyncio.create_task(countdown_timer(context, auction))

        await query.answer(f"✅ Bid placed: {new_bid:.1f} Cr by {team_name}!")
        await query.edit_message_text(
            text=format_player_caption(auction, 20),
            reply_markup=build_bidding_keyboard(True),
            parse_mode=ParseMode.MARKDOWN
        )

# ==============================================================================
# MAIN ENTRYPOINT
# ============================================================================
async def _health_handler(request):
    return web.Response(text="OK - Mock Auction Bot Alive")

async def _health_handler(request):
    return web.Response(text="OK - Mock Auction Bot Alive")

async def _health_handler(request):
    return web.Response(text="OK - Mock Auction Bot Alive")

async def _health_handler(request):
    return web.Response(text="OK - Mock Auction Bot Alive")

async def _health_handler(request):
    return web.Response(text="OK - Mock Auction Bot Alive")

async def _run_bot_and_web():
    web_app = web.Application()
    web_app.router.add_get("/", _health_handler)
    web_app.router.add_get("/health", _health_handler)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"🌐 Health server listening on 0.0.0.0:{PORT}")

    try:
        await asyncio.to_thread(init_db)
        print("✅ Database initialized successfully.")
    except Exception as e:
        print(f"⚠️ init_db error: {e}")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler(["help", "Help"], help_cmd))
    app.add_handler(CommandHandler(["start", "Start"], start_cmd))
    app.add_handler(CommandHandler(["change_auctioneer", "Change_auctioneer"], change_auctioneer_cmd))
    app.add_handler(CommandHandler(["set_conditions", "Set_conditions"], set_conditions_cmd))
    app.add_handler(CommandHandler(["add_owner"], add_owner_cmd))
    app.add_handler(CommandHandler(["remove_owner"], remove_owner_cmd))
    app.add_handler(CommandHandler(["replace_owner"], replace_owner_cmd))
    app.add_handler(CommandHandler(["start_auction", "Start_auction"], start_auction_cmd))
    app.add_handler(CommandHandler(["view_set"], view_set_cmd))
    app.add_handler(CommandHandler(["start_set"], start_set_cmd))
    app.add_handler(CommandHandler(["newplayer"], newplayer_cmd))
    app.add_handler(CommandHandler(["automode"], automode_cmd))
    app.add_handler(CommandHandler(["skip_player", "Skip_player"], skip_player_cmd))
    app.add_handler(CommandHandler(["bring_player"], bring_player_cmd))
    app.add_handler(CommandHandler(["unsold_players", "Unsold_players"], unsold_players_cmd))
    app.add_handler(CommandHandler(["start_unsold_set", "Start_unsold_set"], start_unsold_set_cmd))
    app.add_handler(CommandHandler(["unsold", "Unsold"], unsold_cmd))
    app.add_handler(CommandHandler(["pause_auction", "Pause_auction"], pause_auction_cmd))
    app.add_handler(CommandHandler(["resume_auction", "Resume_auction"], resume_auction_cmd))
    app.add_handler(CommandHandler(["end_auction"], end_auction_cmd))
    app.add_handler(CommandHandler(["purse"], purse_cmd))
    app.add_handler(CommandHandler(["teamlist"], teamlist_cmd))
    app.add_handler(CommandHandler(["myteamlist"], myteamlist_cmd))
    app.add_handler(CommandHandler(["set11"], set11_cmd))
    app.add_handler(CommandHandler(["ranking"], ranking_cmd))
    app.add_handler(CommandHandler(["add_scorer"], add_scorer_cmd))
    app.add_handler(CommandHandler(["remove_scorer"], remove_scorer_cmd))
    app.add_handler(CommandHandler(["add_points"], add_points_cmd))
    app.add_handler(CommandHandler(["set_points"], set_points_cmd))
    app.add_handler(CommandHandler(["top_players"], top_players_cmd))
    app.add_handler(CallbackQueryHandler(callback_handler))

    async with app:
        await app.start()
        await app.updater.start_polling()
        print(f"🏏 Mock IPL/WPL Auction Bot running with health server on port {PORT}...")
        while True:
            await asyncio.sleep(3600)

def main():
    asyncio.run(_run_bot_and_web())

if __name__ == "__main__":
    main()
