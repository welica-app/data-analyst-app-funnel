# Find the step where the most people do not reach the next one

An app team wants people to go through four steps in order. So there are three moves from one step to the next: from step 1 to step 2, from step 2 to step 3, and from step 3 to step 4. The team wants to know at which of these three moves the largest number of people do not reach the next step in the time allowed. You count the people who reach each step, check the counts, and hand over a metric dictionary, a notebook that runs, and a short finding.

## The files

| File | What it holds |
|---|---|
| `app_events.csv` | App events made for this project, not taken from a real app. One row is one action by one person at one time. IDs do not show who anyone is. Times are in UTC, and every person belongs to one of two segments. |
| `event_schema.csv` | Each column in the events file, its type and what it means. |
| `event_catalogue.csv` | Each event name and the app action it records. |
| `funnel_rules.json` | Every rule: the four steps, the two cohort windows to choose from, the 24-hour follow-up, what to do when two actions have the same time, the two ways to remove replays, how to check times, and how drop-off is worked out. |
| `funnel_starter.ipynb` | The notebook. It holds a full worked example that runs and is checked, a first look at your data, blank settings, and your first step already written. |
| `funnel_tools.py` | Helpers the notebook uses to load and check the data, follow each person's actions in time order, count each person once, work out drop-off and save files. |
| `requirements.txt` | What to install for the second way to start. |
| `worked_events.csv` | Separate example data about room bookings. |
| `worked_paths.csv` | For each example user, the events that count at each step, already checked. |
| `worked_counts.csv` | The example's counts and rates, already checked, including a step nobody reached. |
| `spot_check_sample.csv` | Eight users from your data, with space to write which of their events count and where you saw them. |
| `count_template.csv` | A blank grid for the counts and rates, for the whole cohort and each segment, at all four steps. |
| `count_starter.sql` | A start for counting in SQLite, if you choose that way. |
| `metric_dictionary_template.csv` | Blank definitions for the four counts and the three drop-off rates. |
| `finding_template.json` | Blank spaces for your evidence, the segment comparison, a limit, your idea about the cause and the check that could test it. |

## How to start

1. Open this link in a browser: https://github.com/welica-app/data-analyst-app-funnel
2. Press the green **Code** button, then choose **Download ZIP**.
3. Unzip the file. Keep every file name as it is.
4. Open the notebook in one of these two ways.

**First way: Google Colab, in a browser**

1. Open https://colab.research.google.com/ and sign in.
2. Open the **File** menu, choose **Upload notebook**, and pick `funnel_starter.ipynb`.
3. Press **Connect** at the top right.
4. Open the **Files** sidebar (the folder icon on the left). Choose **Upload to session storage**, and upload these eight files: `funnel_tools.py`, `funnel_rules.json`, `app_events.csv`, `event_catalogue.csv`, `spot_check_sample.csv`, `worked_events.csv`, `worked_paths.csv` and `worked_counts.csv`. Put them at the top of the file list, in the folder called `/content`, not inside another folder.
5. Open the **Runtime** menu and choose **Run all**. The example runs. Then the notebook shows the event catalogue and the events of the eight users in `spot_check_sample.csv`.
6. Keep the templates in your downloaded folder for your handover.
7. Before you stop, save the notebook and download any file you made from the **Files** sidebar. A new session needs the eight files uploaded again, to the same place.

**Second way: JupyterLab, on your own computer**

You need Python 3.11 or newer. Open a terminal in this folder.

On macOS or Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
jupyter lab funnel_starter.ipynb
```

On Windows PowerShell:

```sh
py -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
./.venv/Scripts/jupyter.exe lab funnel_starter.ipynb
```

**Then, in the notebook**

1. Fill in `cohort_start`, `cohort_end`, `duplicate_rule`, `focus_segment` and `event_names`, using `funnel_rules.json`.
2. Write the other three steps under the first step, which is already written. Each one is a `next_step` call, as in the example. It takes the eligible people from the step before, and puts its result in `project_steps` under the event name of the step it counts.
3. Set `export_csv = True` to save `project_eligible.csv`, which has one row for each person at each step they reached.
4. Set `count_in_notebook = True` to count in the notebook and save `project_funnel_counts.csv`. Set it to `False` to count in another tool instead.
5. Run the whole notebook again. In Colab, choose **Run all** in the **Runtime** menu. In JupyterLab, choose **Run All Cells** in the **Run** menu.
6. If you set it to `False`, count in one of these. If you used Colab, first download `project_eligible.csv` from the **Files** sidebar into this folder.
   - **SQLite:** you need the SQLite command-line shell installed on your computer. With `project_eligible.csv` in this folder, type `sqlite3 :memory: ".read count_starter.sql"` in a terminal. It counts each step for the whole cohort. You add the segment counts and the rates.
   - **LibreOffice Calc:** open `project_eligible.csv` and `count_template.csv` as comma-separated UTF-8 text. Keep step numbers as numbers, and IDs, event names and times as text. Paste the grid into a second sheet. Count with COUNTIF by step, and with COUNTIFS by step and segment. Fill in the rates using the rule in `funnel_rules.json` for a step nobody reached. Save as ODS to keep the formulas.
