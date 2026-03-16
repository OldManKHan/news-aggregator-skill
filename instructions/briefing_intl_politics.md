# 🌍 International Politics Briefing Instructions (国际时政简报)

> **INPUT**: JSON object with `world_news`, `hn_politics` sections.
> **OUTPUT**: A geopolitical briefing covering major international events, conflicts, diplomacy, and policy changes.

---

## Focus Areas
1. **Conflicts & Security**: Wars, military operations, sanctions, security threats.
2. **Diplomacy**: Summits, treaties, international negotiations.
3. **Policy & Governance**: Elections, legislation, regulatory changes across major economies.
4. **Regional Hotspots**: Middle East, Asia-Pacific, Europe, Americas.

## Anti-Laziness Protocol
1. **Volume**: Output MUST contain at least **15 items** across all sections.
2. **Depth**: For major events, provide **2-3 bullet points** of analysis (background, implications, key players).

## Report Structure

### Part 1: Headlines (Top Stories)
- Top 5 most significant stories across all sources.
- Format:
    ```markdown
    #### 1. [Title (Chinese Translation)](url)
    - **Source**: BBC World | **Time**: 2h ago
    - **Summary**: One sentence Chinese summary.
    - **Deep Dive**: Background context + geopolitical implications.
    ```

### Part 2: Regional Breakdown
- Group remaining stories by region (Middle East, Europe, Asia-Pacific, Americas, Africa).
- Use concise format with source attribution.

### Part 3: HN Discussion Highlights
- Notable political discussions from Hacker News with community sentiment.
