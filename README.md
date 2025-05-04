# BigDataBot 🧠📈  
AI-driven analysis of meme tokens on pump.fun using blockchain data.

## Overview

**BigDataBot** is an experimental AI project that explores predictive ml models for crypto tokens on [pump.fun](https://pump.fun/). 
It uses data from [Dune](https://dune.com/) data to identify promising meme coins in their early stages using machine learning.

The project pulls aggregated data via **Dune Analytics**, and trains a classifier model to detect potential "winners" based on early market and wallet dynamics.

## Features

- 📊 **Data Pipeline**  
  1. Use Dune SQL to aggregate trade data and find promising wallets
  2. Clean data using python 
  3. Feature engineering using python
  4. Train ML Model on data 
  5. Use unseen data to evaluate model in a backtest fashion 

- 🧠 **ML Models**  
  - Binary classifier trained to predict meme token success.
  - Monte Carlo Tree search for potential trading strategy optimization.

- ⚙️ **Tech Stack**
  - Python, scikit-learn, pandas, matplotlib
  - Dune Analytics
  - Doker for deployment

## Use Cases

- Early identification of high-potential meme tokens
- Exploratory analysis of behavioral patterns on pump.fun
- Framework for future AI-based crypto trading tools

## Status

This project is a proof of concept and **not intended for financial advice or production use**.  
Future plans may include real-time inference and web-based dashboards.

## Getting Started

1. Clone the repo  
   ```bash
   git clone https://github.com/your-username/BigDataBot.git
   cd BigDataBot
   ```

2. Add .env file with your own dune credentials
3. Run alpha_wallet_pipeline scripts

## Disclaimer

This project is for research and educational purposes only. Cryptocurrency investments carry risk.
Do your own research.

## License

MIT License
