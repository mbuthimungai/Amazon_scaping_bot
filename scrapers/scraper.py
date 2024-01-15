from tools.tool import TryExcept, Response, yaml_load, userAgents, domain
from bs4 import BeautifulSoup
import re


class Amazon:
    """
    The Amazon class provides methods for scraping data from Amazon.com.

    Attributes:
        headers (dict): A dictionary containing the user agent to be used in the request headers.
        catch (TryExcept): An instance of TryExcept class, used for catchig exceptions.
        scrape (yaml_load): An instance of the yaml_load class, used for selecting page elements to be scraped.
    """

    def __init__(self, userInput):
        """
        Initializes an instance of the Amazon class.
        """
        self.userInput = userInput
        self.country_domain = domain(userInput) # Extract the country domain from the Amazon URL.
        self.headers = {'User-Agent': userAgents()}
        self.catch = TryExcept()        
        self.scrape = yaml_load('selector')
        self.pages_search_links = []

    async def status(self):
        response = await Response(self.base_url).response()
        return response

    async def getASIN(self):
        """
        Extracts the ASIN (Amazon Standard Identification Number) from the given URL.

        Args:
            url (str): The URL to extract the ASIN from.

        Return:
            str: The ASIN extracted from the URL.

        Raises:
            IndexError: If the ASIN cannot be extracted from the URL.
        """
        pattern = r"(?<=dp\/)[A-Za-z|0-9]+"
        try:
            asin = (re.search(pattern, self.userInput)).group(0)
        except Exception as e:
            asin = "N/A"                
        return asin
    
    async def extractProductData(self, content):
        """
        Helper method to extract product information from the Amazon product page content.

        Args:
            -content (str): The HTML content of the product page.

        Returns:
            -dict: A dictionary containing product information.
        """
        soup = BeautifulSoup(content, 'lxml')
        try:
            image_link = soup.select_one(self.scrape['image_link_i']).get('src')
        except Exception as e:
            image_link = soup.select_one(self.scrape['image_link_ii']).get('src')

        try:
            availabilities = soup.select_one(self.scrape['availability']).text.strip()
        except AttributeError:
            availabilities = 'In stock'

        store = await self.catch.text(soup.select_one(self.scrape['store']))
        store_link = f"https://www.amazon.{self.country_domain}{await self.catch.attributes(soup.select_one(self.scrape['store']), 'href')}"

        return {
            'Name': await self.catch.text(soup.select_one(self.scrape['name'])),
            'ASIN': await self.getASIN(),
            'Price': await self.catch.text(soup.select_one(self.scrape['price_us'])),
            'Rating': await self.catch.text(soup.select_one(self.scrape['review'])),
            'Rating count': await self.catch.text(soup.select_one(self.scrape['rating_count'])),
            'Availability': availabilities,
            'Hyperlink': self.userInput,
            'Image': image_link,
            'Store': store,
            'Store link': store_link,
        }

    async def dataByAsin(self):
        """
        Extracts product information from the Amazon product page by ASIN.
        """
        link_to_product = f"https://www.amazon.com/dp/{self.userInput}"        
        content = await Response(link_to_product).content()
        
        return await self.extractProductData(content)

    async def dataByLink(self):
        """
        Extracts product information from the Amazon product page by direct link.
        """        
        content = await Response(self.userInput).content()
        return await self.extractProductData(content)
    
    async def find_links_with_aria_label(self):
        """
        Parses HTML content and finds all links (<a> tags) whose aria-label attribute contains a specific substring.
        
        :return: A list of href values from the matched <a> tags.
        """
        content = await Response(self.userInput).content()
        soup = BeautifulSoup(content, 'lxml')

        # Define a function to check if 'aria-label' contains the specified substring
        def has_go_to_page(tag):
            return tag.name == 'a' and tag.has_attr('aria-label') and "Go to page " in tag['aria-label']

        # Find all elements with 'aria-label' containing the specified substring
        elements = soup.find_all(has_go_to_page)

        # Extract the href attributes
        links = [f"https://www.amazon.com/{element['href']}" for element in elements]

        return links

    
    async def product_links(self) -> set:
        """
            Extract product links from the Amazon product search page.
            
            Returns:
                - list: An array containing the scraped products information
                 
        """
        
        content = await Response(self.userInput).content()
        soup = BeautifulSoup(content, "lxml")   
                
        # Find all elements with 'data-asin' attribute
        elements_with_asin = soup.find_all(lambda tag: tag.has_attr('data-asin'))        
        # Create a set to store unique ASINs
        unique_asins = set()
        # Extract ASINs and add them to the set
        for element in elements_with_asin:            
            asin = element['data-asin']
            unique_asins.add(asin)
        
        return unique_asins
        
    async def product_review(self):
        """
            Extracts product reviews from the Amazon product reviews page.

            Returns:
                -dict: A dictionary containing product review information, including top positive and top critical reviews.

            Raises:
                -AttributeError: If the review information cannot be extracted from the page.
        """
        # Get ASIN asynchronously:
        asin = await self.getASIN()
        # From the URL for Amazon product reviews:
        review_url = f"https://www.amazon.{self.country_domain}/product-reviews/{asin}"        
        req = await Response(review_url).content()
        soup = BeautifulSoup(req, 'lxml')
        pos_crit_review = soup.select_one(self.scrape['pos_criti_review'])
        review_lists = soup.select_one(self.scrape['review_lists']).text.strip()
        # Check if positive and critical reviews are present
        if pos_crit_review is not None:
            profile_name = soup.select(self.scrape['profile_name'])
            review_title = soup.select(self.scrape['full_review'])
            stars = soup.select(self.scrape['stars'])
            review_title = soup.select(self.scrape['review_title'])
            full_review = soup.select(self.scrape['full_review'])
            product = soup.select_one(self.scrape['product_name']).text.strip()
            image = soup.select_one(self.scrape['image']).get('src')
            # Populate datas dictionary for positive and critical reviews
            datas = {
                'top positive review':
                    {
                        'product': product,
                        'customer': profile_name[0].text.strip(),
                        'stars': stars[0].text.strip(),
                        'title': review_title[0].text.strip(),
                        'review': full_review[0].text.strip(),
                        'image': image,
                    },
                'top critical review':
                    {
                        'product': product,
                        'customer': profile_name[-1].text.strip(),
                        'stars': stars[-1].text.strip(),
                        'title': review_title[-1].text.strip(),
                        'review': full_review[-1].text.strip(),
                        'image': image,
                    }
            }
        # Check if there are no positive and critical reviews, but there are review lists
        elif pos_crit_review is None and review_lists != "":
            profile_name = soup.select(self.scrape['profile_name'])
            review_title = soup.select(self.scrape['full_review'])
            stars = soup.select(self.scrape['stars_i'])
            review_title = soup.select(self.scrape['review_title_i'])
            full_review = soup.select(self.scrape['full_review_i'])
            product = soup.select_one(self.scrape['product_name']).text.strip()
            image = soup.select_one(self.scrape['image']).get('src')
            datas = {
                'top positive review':
                    {
                        'product': product,
                        'customer': profile_name[0].text.strip(),
                        'stars': stars[0].text.strip(),
                        'title': review_title[0].text.strip(),
                        'review': full_review[0].text.strip(),
                        'image': image,
                    },
                'top critical review':
                    {
                        'product': product,
                        'customer': profile_name[-1].text.strip(),
                        'stars': stars[-1].text.strip(),
                        'title': review_title[-1].text.strip(),
                        'review': full_review[-1].text.strip(),
                        'image': image,
                    }
            }
        # Handle the case where there are no reviews
        else:
            datas = soup.select_one(self.scrape['no_reviews']).text.strip()
        return datas

