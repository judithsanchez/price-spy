# Spec: The Manual Price Spy (Slice 1)

This document outlines the specifications for "Slice 1" of the Price Spy project. The focus of this slice is on building the core price extraction engine, which is triggered manually.

## 1. The Manual Spy

This initial version of the tool will run on-demand, without any scheduling or periodic checking features. It will be executed manually by the user, and its primary purpose is to extract price information from a given URL.

## 2. Data Flow

The data flow for Slice 1 is as follows:

1.  **Input:** The user provides a product URL via a Command Line Interface (CLI).
2.  **Processing:** The tool will fetch the content of the URL, and use a combination of techniques to identify and extract the price.
3.  **Output:** The tool will output a structured JSON object to the console (stdout) containing the extracted information.

## 3. AI-Powered Extraction

The core of the price extraction will be an "AI-Powered" engine.

### 3A. Universal Approach

The tool will be designed to be "universal", using Computer Vision to analyze web pages. This will allow it to work on a wide variety of websites without needing to write custom scrapers for each one.

### 3B. Stealth Context

The tool will be optimized for European/Dutch locales, with specific tuning for these regions.

### 3C. Dual-Mode AI Prompt

The extraction engine will be capable of handling two types of URLs:
*   A direct URL to a specific product page (e.g., on Amazon).
*   A URL to a search results page that lists multiple products (e.g., on Google Shopping).

## 4. Output Data Structure

The output of the tool will be a JSON object printed to standard output. The structure of this JSON object will be defined at a later stage. For now, the focus is on extracting the price.

## 5. Project Slice: Slice 1

This specification is for "Slice 1" of the project. Future slices may include features like:
*   Storing the price data in a database (e.g., SQLite).
*   Scheduling periodic price checks.
*   A graphical user interface (GUI).

## 6. Target Websites

For verification and testing purposes, the tool will be explicitly tested against the following websites:
*   Amazon
*   Google Shopping
*   Kruidvat
*   Bol.com