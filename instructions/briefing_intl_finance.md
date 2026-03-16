# 💹 International Finance Briefing Instructions (国际金融简报)

> **INPUT**: JSON object with `global_markets`, `cn_finance` sections.
> **OUTPUT**: A global finance briefing covering markets, central bank policy, commodities, and macro trends.

---

## Focus Areas
1. **Markets**: Equities, bonds, forex, crypto movements and drivers.
2. **Central Banks**: Fed, ECB, BOJ, PBOC policy signals and rate decisions.
3. **Commodities & Energy**: Oil, gold, metals, agricultural commodities.
4. **Macro Trends**: GDP, inflation, employment, trade data across major economies.

## Anti-Laziness Protocol
1. **Volume**: Output MUST contain at least **15 items** across all sections.
2. **Depth**: For market-moving events, provide **2-3 bullet points** (what happened, why it matters, what to watch next).

## Report Structure

### Part 1: Market Movers (Top Stories)
- Top 5 most market-impactful stories.
- Format:
    ```markdown
    #### 1. [Title (Chinese Translation)](url)
    - **Source**: Bloomberg Markets | **Time**: 1h ago
    - **Summary**: One sentence Chinese summary.
    - **Market Impact**: Which assets/sectors affected and direction.
    ```

### Part 2: Global Markets Overview
- Group by theme: Equities, Fixed Income, Forex, Commodities, Crypto.

### Part 3: China & Asia Focus
- Stories from WallStreetCN and Asia-specific sources.
