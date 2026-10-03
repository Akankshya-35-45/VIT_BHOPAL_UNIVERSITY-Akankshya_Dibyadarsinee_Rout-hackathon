# Data Sources & Assumptions

## Public / live source
- **GDELT DOC 2.0 API:** public news metadata and article-list search used for live ingestion.
- **NewsAPI:** optional second live news source. The application uses it only when `NEWSAPI_KEY` is configured.

## Synthetic sources
- `data/social_posts.csv`: synthetic social-media-style posts created for reproducible demonstration. They are not copied from real users.
- `data/portfolio.csv`: synthetic wholesale-banking-style portfolio containing equities, bonds, loans and derivatives.

## Modeling assumptions
- Sentiment is normalized to the VADER compound score in [-1, 1].
- Event classification uses a transparent domain taxonomy and keyword evidence.
- Impact is a 1–10 prototype severity score; it is not a market forecast.
- Stress shocks are illustrative scenario assumptions and are not investment advice.
- No proprietary or confidential S&P Global / CRISIL data is used.
