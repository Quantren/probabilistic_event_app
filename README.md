## About the Project

Probabilistic Event Generator with Database

Wordy name, simple functionality. For my final project I have developed a simple Flask app that generates an index, an outcome, and a history page, and through these components (along with some simple Python and HTML), the user is able to generate outcomes from probabilistic events over an N number of draws for a variables number of faces (2 min/max for a coin, 4 min for a dice roll). Additionally, as it was simple and added fun functionality, the ability to weight the coin was added to the coin was also included.

This project is the perfect engine for probabilistic simulation, aid for game nights when playing board games with missing mediums, or just an idle time-waster (something we rarely lack, nowadays).

If tracking is enabled, output is saved to a simple SQLite DB, and output can be viewed through queries (not implemented) or by navigating to the /history page in the app. At this page, one can clear the database through a nifty danger button, filter results based on the event types available in the db file, or just view the most recent 100 simulations.

Quick Discussion -

For Python, OOP was implemented to define what an Event was, and that definition was passed onto both a Coin and Die class, which contained the attributes germane to each probabilistic medium, as well as the implementation for perform (which represents a flip or roll).

A factory is then implemented through the event_factory function; after a simple check for the event that is requested, additional parameters are retrieved and passed into the relevant class, which is then instantiated with that information and returned.

Usage:

1. Navigate to the project directory in a terminal.
2. run, "source .venv/bin/activate" (or create venv from requirements.txt, found in the root of the project directory)
3. run, "python3 app.py"
4. navigate to the URL that is provided in the terminal.
5. set event type desired, set attributes, run, rerun, observe the results, enjoy!
