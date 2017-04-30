# keyword-scraper
A basic web scraper that grabs keywords and occurrence counts and saves for later use.

Made to be easily configurable to use for any site by editing config.json to contain 
basic site access information and then a list of pages to scrape. Currently supports
both explicit URL paths as well as reference type paths, which will use links found
in a previous page as the target for a subsequent page.

This program uses the config values and strategy patterns for the type of scrape
analysis to perform, as well as the output format, so it should be easily
modified to dump results into a DB instead of a CSV file or implement custom analysis
logic on the scrape results.
