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
  4. Train ML models on historical data
  5. Evaluate performance on unseen data in a backtesting-style workflow  

- 🧠 **ML Models**  
  - Binary classifier trained to predict meme token success.
  - Monte Carlo Tree Search to explore and optimize trading strategies

- 🚀 **Production**  
  - Listens to wallet events in real-time via Solana WebSockets (alpha wallet tracking)  
  - Retrieves live chart data using BirdEye’s data service  
  - Executes trades through Solana RPC via the Jupiter Aggregator API  

- ⚙️ **Tech Stack**
  - Python, scikit-learn, pandas, matplotlib
  - Dune Analytics for data sourcing
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
