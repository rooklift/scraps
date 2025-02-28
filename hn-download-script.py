#!/usr/bin/env python3

# Written by Claude

import sys
import re
import requests
import json
import io
import os
import html
import pathlib

def get_unique_filename(base_filename):
	"""Generate a unique filename by adding (1), (2), etc. before the extension if needed."""
	if not os.path.exists(base_filename):
		return base_filename

	path = pathlib.Path(base_filename)
	directory = path.parent
	stem = path.stem
	suffix = path.suffix

	counter = 1
	while True:
		new_filename = os.path.join(directory, f"{stem}({counter}){suffix}")
		if not os.path.exists(new_filename):
			return new_filename
		counter += 1

def html_decode(text):
	"""Decode HTML entities in text."""
	if text:
		return html.unescape(text)
	return text

def extract_comments(item, comments, depth=0):
	"""Recursively extract and decode comments from an item with threading depth.

	Args:
		item: The comment item to process
		comments: List to collect comment data
		depth: Current depth in the comment tree (0 = top level)
	"""
	if "text" in item and item["text"]:
		prefix = ">" * depth  # Add '>' characters based on depth
		decoded_text = html_decode(item["text"])

		# Store both the depth and text for later processing
		comments.append({
			"depth": depth,
			"text": decoded_text,
			"author": item.get("author", "anonymous"),
			"id": item.get("id", "")
		})

	if "children" in item and item["children"]:
		for child in item["children"]:
			extract_comments(child, comments, depth + 1)

def main():
	# Fix Unicode encoding issues on Windows
	if sys.platform == "win32":
		sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

	# Set default encoding to utf-8 for file operations
	sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")

	# Check if argument is provided
	if len(sys.argv) != 2:
		print("Usage: python script.py <item_id_or_json_file>")
		sys.exit(1)

	arg = sys.argv[1]

	# Initialize data variable
	data = None

	# Check if the argument could be a file
	if os.path.exists(arg):
		try:
			with open(arg, "r", encoding="utf-8") as file:
				data = json.load(file)
			print(f"Loaded data from file: {arg}")
		except json.JSONDecodeError:
			print(f"Error: {arg} is not a valid JSON file.")
			sys.exit(1)
	else:
		# If not a file, check if it's a valid item ID
		if not re.match(r"^[0-9]+$", arg):
			print("Please provide a valid integer as the item ID or a valid JSON file path.")
			sys.exit(1)

		item_id = arg

		# Make API call to Hacker News Algolia API
		try:
			response = requests.get(f"https://hn.algolia.com/api/v1/items/{item_id}")

			# Check if the request was successful
			if response.status_code != 200:
				print(f"Error: Failed to fetch data. Status code: {response.status_code}")
				sys.exit(1)

			# Parse the JSON response
			data = response.json()
		except requests.RequestException as e:
			print(f"Error: Failed to connect to the API: {e}")
			sys.exit(1)

	# Ensure we have valid data
	if not data:
		print("Error: No valid data found.")
		sys.exit(1)

	# Generate unique output filenames
	json_output_file = get_unique_filename("data.json")
	comments_output_file = get_unique_filename("comments.txt")

	# Save the raw JSON data
	"""
	with open(json_output_file, "w", encoding="utf-8") as outfile:
		json.dump(data, outfile, ensure_ascii=False, indent=2)
	print(f"Saved raw data to: {json_output_file}")
	"""

	# Extract all comment texts with threading information
	comments = []
	extract_comments(data, comments)

	# Write comments to the output file
	with open(comments_output_file, "w", encoding="utf-8") as outfile:
		for comment in comments:
			depth = comment["depth"]
			prefix = ">" * depth

			# Add prefix at the beginning of each line in multi-line comments
			lines = comment["text"].split("\n")
			formatted_lines = [(prefix + " " + line if line.strip() else line) for line in lines]
			formatted_text = "\n".join(formatted_lines)

			# Add author info at the top of each comment
			author_line = f"{prefix} @{comment['author']} (id: {comment['id']})"
			outfile.write(author_line + "\n")
			outfile.write(formatted_text + "\n\n")

	print(f"Saved {len(comments)} comments to: {comments_output_file}")

	# Print all comments
	for comment in comments:
		depth = comment["depth"]
		prefix = ">" * depth

		# Add prefix at the beginning of each line
		lines = comment["text"].split("\n")
		formatted_lines = [(prefix + " " + line if line.strip() else line) for line in lines]
		formatted_text = "\n".join(formatted_lines)

		# Add author info
		author_line = f"{prefix} @{comment['author']} (id: {comment['id']})"
		print(author_line)
		print(formatted_text + "\n")

if __name__ == "__main__":
	main()
