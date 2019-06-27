# Fin-Analysis
Time series analysis for whatever financial instrument I'm currently interested in

# 10-year treasury yield project
This project is based off the observation that the copper/gold ratio has an uncanny correlation with 10-year Treasury yields. This observation was made by Jeffrey Gundlach and Adam Robinson. Adam explains that when metals traders expect the economy to expand they tend to buy copper since it has many industrial uses. When the economy is expected to contract, they tend to buy Gold since it is considered a safe-haven asset. Accordingly, the fed tends to raise interest rates when the economy is expected to expand, and decrease interest rates when the economy is expected to contract. The 10-year Treasury yield is used since it is a benchmark used for many common loans such as a mortgage. In other words, these are both measures of economic growth expectations. 

Adam also goes on to explain that the corporate bond etf to treasury bond etf ratio(LQD/IEF) is the same expression from the bond traders point of view, and the financial sector etf to utilities sector etf(IYF/IDU) is the same expression from the equity traders point of view. 

In this project I use rolling regression to find the rolling correlations for these variables. 

To do:
- Visualize these relationships within different time frames, and identify the most effective ones
- Predict the direction of interest rates
