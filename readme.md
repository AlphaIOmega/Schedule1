# Drug Lab - Product Viewer

A web application that allows you to view, analyze, and compare products from the game "Schedule I" (previously known as "Drug Dealer Simulator 2").

## Overview

This tool helps you:

- View all your discovered products and their properties
- Calculate production costs and profit margins
- Analyze crafting recipes and mixing paths
- Compare cost efficiency between different products
- Filter and search your product collection
- Visualize effects and properties

## Setup Instructions

### Prerequisites

- [Python 3.7 or higher](https://www.python.org/downloads/) - Download and install from python.org
- Web browser (Chrome, Firefox, Edge, etc.)

### Quick Start (Easy Method)

1. Download or clone this repository:
   - Click the green "Code" button at the top of the GitHub page
   - Select "Download ZIP"
   - Extract the ZIP file to a location on your computer

2. Replace the sample data with your game data:
   - Run the included `SavesOpener.bat` file to open your game's save folder
   - Copy your `Products.json` file to the `data` folder in this application
   - Copy your entire `CreatedProducts` folder to the `data` folder in this application

3. Run the application using the included `StartApp.bat` file:
   - Double-click on `StartApp.bat` in the main folder
   - This will automatically install Flask if needed and start the application
   - Your web browser should open automatically

4. If the browser doesn't open automatically, go to:
   ```
   http://127.0.0.1:5000/
   ```

### Detailed Installation Method (For Advanced Users)

1. Clone or download this repository to your local machine:
   ```
   git clone https://github.com/username/drug-lab-product-viewer.git
   cd drug-lab-product-viewer
   ```

2. Install the required Python packages:
   - Open Command Prompt or PowerShell in the application folder
   - Run the following command:
   ```
   pip install flask
   ```

3. Replace the sample data files with your own game data:
   - First, run the included `SavesOpener.bat` file to open your game's save folder
     - This opens: `%localappdata%\low\tvgs\Schedule I\Saves\`
   - Navigate to your specific save folder (each save has its own folder)
   - From your save folder, copy these files to the application:
     - `Products.json` file → Copy to the `data` folder in this application
     - `CreatedProducts` folder → Copy the entire folder to the `data` folder

4. Start the application:
   - In Command Prompt or PowerShell, make sure you're in the application folder
   - Run this command:
   ```
   python app.py
   ```

5. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## Optional: Create Shortcut to Start the App

If you want to create a permanent shortcut to launch the application:

1. Right-click on the desktop or in a folder and select New > Shortcut
2. For the location, enter:
   ```
   cmd.exe /c "cd /d [PATH_TO_YOUR_APP_FOLDER] && python app.py"
   ```
   Replace `[PATH_TO_YOUR_APP_FOLDER]` with the actual path to your app folder
3. Name the shortcut "Schedule I Product Viewer" or something similar
4. Right-click the shortcut and select Properties
5. Click on "Change Icon" and select an appropriate icon if desired
6. Click OK and Apply

## Using Your Own Game Data

The directory structure should look like:
```
drug-lab-product-viewer/
├── app.py
├── effects.py
├── SavesOpener.bat
├── StartApp.bat                      <-- New file to easily start the app
├── data/
│   ├── Products.json                  <-- Replace with your file
│   ├── agriculture_consumables.json
│   ├── base_costs.json
│   ├── effects.json
│   └── CreatedProducts/               <-- Replace with your folder
│       ├── afghancake.json
│       ├── biocrack.json
│       └── [all your product files]
├── static/
│   ├── css/
│   └── js/
└── templates/
```

## Features

### Product Listing
- View all your discovered products in a grid
- Sort by name, price, mix count, and efficiency
- Filter by drug type (weed, meth, cocaine)
- Search for specific products

### Advanced Filtering
- Filter by mix count (complexity)
- Filter by effects (like "Energizing", "Athletic", etc.)
- Combine filters for precise results

### Product Details
- View detailed information about each product:
  - Visual appearance (colors)
  - Properties and effects
  - Complete crafting recipe chain
  - Cost analysis and profit calculations

### Agriculture Calculator
- Calculate production costs for growing:
  - Different soil types
  - Additives (PGR, Speedgrow, Fertilizer)
  - Pseudo types (for meth production)
- See yields and cost per unit

### Theme Switching
- Switch between light and dark mode for comfortable viewing

## Troubleshooting

- **Missing Products**: Make sure you've copied both Products.json AND the CreatedProducts folder
- **Application Won't Start**: 
  - Check that you've installed Python correctly (run `python --version` in cmd to verify)
  - Check that you've installed Flask (`pip install flask`)
  - Try running the StartApp.bat file which will install Flask if needed
- **Blank Page**: Verify your Products.json file is valid and not corrupted
- **Calculation Errors**: Ensure your data files are from a compatible game version
- **Port Already in Use**: If you see "Address already in use" error, close any other instances of the app or change the port in app.py

## Notes

- This application is for informational purposes only and works offline
- No data is sent to any external servers
- All calculations are performed locally in your browser
- The application does not modify your game saves

---

*Drug Lab - Product Viewer is an unofficial fan tool and is not affiliated with TVGS or the creators of Schedule I/Drug Dealer Simulator 2.*