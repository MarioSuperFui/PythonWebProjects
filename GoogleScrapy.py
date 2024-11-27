import feedparser
import tkinter as tk
from tkinter import ttk
from bs4 import BeautifulSoup  # For cleaning HTML content
import webbrowser
from datetime import datetime

class NewsApp:
    def __init__(self, master, rss_url):
        self.master = master
        self.master.title("Google News Reader")
        self.master.geometry("800x600")

        # Apply ttk Theme
        style = ttk.Style()
        style.theme_use("clam")  # You can change this to "alt", "classic", "vista", etc.

        # Title Label
        self.title_label = ttk.Label(master, text="📰 Google News Reader", font=("Helvetica", 18, "bold"))
        self.title_label.pack(pady=10)

        # Filter and Open Link Buttons Frame (Top-right placement)
        self.filter_frame = ttk.Frame(master, padding=(10, 10))
        self.filter_frame.pack(fill="x", pady=5)

        self.keyword_entry = ttk.Entry(self.filter_frame, font=("Helvetica", 12))
        self.keyword_entry.pack(side="left", padx=5, fill="x", expand=True)

        self.filter_button = ttk.Button(self.filter_frame, text="Apply Filter", command=self.apply_filter)
        self.filter_button.pack(side="left", padx=5)

        self.open_link_button = ttk.Button(self.filter_frame, text="Open Link in Browser", command=self.open_selected_link, state="disabled")
        self.open_link_button.pack(side="right", padx=5)

        # News List Frame
        self.frame = ttk.Frame(master)
        self.frame.pack(fill="both", expand=True)

        # Scrollable Listbox
        self.news_listbox = tk.Listbox(self.frame, font=("Helvetica", 12), height=25, width=80, activestyle="dotbox")
        self.news_listbox.pack(side="left", fill="both", expand=True)

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.news_listbox.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.news_listbox.config(yscrollcommand=self.scrollbar.set)

        # News Details Frame
        self.details_frame = ttk.LabelFrame(master, text="News Details", padding=(10, 10))
        self.details_frame.pack(fill="x", pady=10)

        self.details_label = ttk.Label(self.details_frame, text="Select an article to view details", font=("Helvetica", 14), wraplength=700, anchor="w", justify="left")
        self.details_label.pack()

        # Label for Publication Date
        self.pub_date_label = ttk.Label(self.details_frame, text="", font=("Helvetica", 12), anchor="w", justify="left")
        self.pub_date_label.pack(pady=5)

        # Scrollable Text Box for the Summary
        self.summary_text = tk.Text(self.details_frame, font=("Helvetica", 12), wrap="word", height=8, width=80, padx=10, pady=10)
        self.summary_text.pack(fill="both", expand=True)

        # Scrollbar for the Text Box
        self.summary_scrollbar = ttk.Scrollbar(self.details_frame, orient="vertical", command=self.summary_text.yview)
        self.summary_scrollbar.pack(side="right", fill="y")
        self.summary_text.config(yscrollcommand=self.summary_scrollbar.set)

        # RSS Feed URL
        self.rss_url = rss_url

        # News Data
        self.news_items = []  # All news entries
        self.filtered_news_items = []  # Filtered news entries

        # Populate Listbox
        self.fetch_and_display_news()

        # Bind Listbox Selection Event
        self.news_listbox.bind("<<ListboxSelect>>", self.display_news_details)

        # Initialize the selected link
        self.selected_link = None

    def fetch_and_display_news(self):
        """Fetch and display news titles from the RSS feed."""
        feed = feedparser.parse(self.rss_url)
        self.news_items = []  # Reset the news items list

        for entry in feed.entries:
            self.news_items.append({"entry": entry})

        # Display the filtered news (all news by default)
        self.display_filtered_news(self.news_items)

    def display_filtered_news(self, news_list):
        """Display a given list of news items in the listbox."""
        self.news_listbox.delete(0, tk.END)  # Clear the listbox

        for item in news_list:
            entry = item["entry"]
            self.news_listbox.insert(tk.END, f"📰 {entry.title}")

        self.filtered_news_items = news_list

    def clean_summary(self, summary):
        """Remove any HTML tags or links from the summary."""
        soup = BeautifulSoup(summary, "html.parser")
        return soup.get_text()

    def display_news_details(self, event):
        """Display details of the selected news item."""
        selected_index = self.news_listbox.curselection()
        if not selected_index:
            return

        index = selected_index[0]
        selected_news = self.filtered_news_items[index]["entry"]

        # Get details
        title = selected_news.title
        summary_raw = selected_news.summary if "summary" in selected_news else "No summary available"
        summary_clean = self.clean_summary(summary_raw)

        # Get the publication date and format it
        pub_date_raw = selected_news.published if "published" in selected_news else "No publication date"
        pub_date = self.format_pub_date(pub_date_raw)

        # Enable the open link button
        self.open_link_button.config(state="normal")
        self.selected_link = selected_news.link  # Store the link for opening in the browser

        # Display details
        self.details_label.config(text=f"Title: {title}")

        # Display the cleaned summary in the scrollable text widget
        self.summary_text.delete(1.0, tk.END)  # Clear the current text
        self.summary_text.insert(tk.END, summary_clean)  # Insert the cleaned summary

        # Display the publication date
        self.pub_date_label.config(text=f"Published on: {pub_date}")

    def format_pub_date(self, pub_date):
        """Format the publication date into a more human-readable form."""
        try:
            # Parse the publication date string into a datetime object
            pub_date_obj = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
            # Return a formatted date string
            return pub_date_obj.strftime("%B %d, %Y at %I:%M %p")
        except ValueError:
            return pub_date  # Return the raw date if it can't be parsed

    def open_selected_link(self):
        """Open the selected news link in the default web browser."""
        if self.selected_link:
            webbrowser.open(self.selected_link)

    def apply_filter(self):
        """Filter news items based on the keyword entered by the user."""
        keyword = self.keyword_entry.get().strip().lower()

        filtered = []
        for item in self.news_items:
            entry = item["entry"]

            # Filter by keyword
            if keyword in entry.title.lower() or (hasattr(entry, "summary") and keyword in entry.summary.lower()):
                filtered.append(item)

        # Display the filtered news
        self.display_filtered_news(filtered)


# Main Application
if __name__ == "__main__":
    root = tk.Tk()
    app = NewsApp(root, "https://news.google.com/rss")
    root.mainloop()
