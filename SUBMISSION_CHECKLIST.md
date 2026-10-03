# S&P Global & CRISIL Campus Hackathon 2026 — Final Submission Checklist

## A. Local validation
- [ ] Python 3.11+ installed
- [ ] Create and activate `.venv`
- [ ] `pip install -r requirements.txt` completes
- [ ] `streamlit run app.py` opens dashboard
- [ ] Live GDELT signals appear OR synthetic social feed appears
- [ ] Manual analyzer returns sentiment/event/impact
- [ ] Select Geopolitical + impact 8 + threshold 7
- [ ] Run Stress Test and verify before/after/P&L/table
- [ ] `uvicorn src.api:app --reload` starts successfully
- [ ] `/health` returns `{"status":"ok"}`
- [ ] `/analyze` returns structured risk JSON

## B. GitHub packaging
- [ ] Repository name: `vit-bhopal-akankshya-dibyadarsinee-rout-hackathon`
- [ ] Repository is PUBLIC
- [ ] README.md at root
- [ ] requirements.txt at root
- [ ] LICENSE at root
- [ ] src/ contains application code
- [ ] data/ contains all CSV/JSON demo data
- [ ] docs/presentation.pdf exists and has 7 slides
- [ ] docs/architecture.png exists
- [ ] No `.env` or API keys committed
- [ ] No confidential/proprietary S&P Global or CRISIL data
- [ ] No large unnecessary binaries
- [ ] Make several incremental commits if time permits

## C. README
- [ ] Candidate name filled
- [ ] College email filled
- [ ] College/campus filled
- [ ] Demo YouTube URL added
- [ ] Slide deck link added if needed
- [ ] Quickstart tested exactly as written
- [ ] Dataset assumptions documented
- [ ] Domain impact documented

## D. Demo video
- [ ] Keep around 5–7 minutes; maximum allowed by the supplied guideline is 10 minutes
- [ ] 0:00–0:30 problem + solution
- [ ] 0:30–1:00 README setup/run
- [ ] 1:00–3:30 end-to-end NLP flow
- [ ] 3:30–5:00 stress test
- [ ] 5:00–6:00 API + architecture
- [ ] 6:00–7:00 results/impact/limitations
- [ ] Upload to YouTube as UNLISTED
- [ ] Test URL in an incognito/private browser window

## E. Presentation
- [ ] 7-slide PDF is included at `docs/presentation.pdf`
- [ ] Slide 1 title/candidate/college
- [ ] Slide 2 problem + approach
- [ ] Slide 3 architecture + data flow
- [ ] Slide 4 implementation highlights
- [ ] Slide 5 key results
- [ ] Slide 6 domain impact
- [ ] Slide 7 limitations + next steps

## F. Final submission
- [ ] Copy final public GitHub URL
- [ ] Copy final unlisted YouTube URL
- [ ] Submit through official form
- [ ] Open GitHub URL in incognito
- [ ] Open YouTube URL in incognito
- [ ] Verify final commit timestamp is before deadline
- [ ] Save a screenshot of the successful submission confirmation
