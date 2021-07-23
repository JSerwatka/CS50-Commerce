# CS50-Commerce

## Table of contents
- [Description and requirements](#description-and-requirements)
- [Preview](#preview)
- [Installation](#installation)

## Description and requirements
Design an eBay-like e-commerce auction site that will allow users to post auction listings, place bids on listings, comment on those listings, and add listings to a “watchlist.”

All requirements can be viewed here: https://cs50.harvard.edu/web/2020/projects/2/commerce/

Live version can be viewed here: http://cs50commerce.pythonanywhere.com/

## Preview
### View Listings
![all](https://user-images.githubusercontent.com/33938646/126637562-180a7695-5a0a-4811-85dc-d99fc2fc46ff.gif)

### View Listing Page
![listing-page](https://user-images.githubusercontent.com/33938646/126637572-fb34d5e8-d5f5-4e95-b54e-0c58ee6344fe.gif)

## Installation
To set up this project on your computer:
1. Download this project
    ```
    gti clone https://github.com/JSerwatka/CS50-Commerce.git
    ```
2. Install all necessary dependencies
    ```
    pip install -r requirements.txt
    ```
3. Make migrations
    ```
    python manage.py makemigrations
    ```
4. Migrate
    ```
    python manage.py migrate
    ```

---
Special thanks to Brian and the entire CS50 team for making learning easy, engaging, and free. 
