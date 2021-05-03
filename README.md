# We Cook - Recipe and community cooking website
This is a website where users can add recipes or search for recipes other users have added.

[Link to live project](https://we-cook-recipe-sharing.herokuapp.com/)

---

### User Stories:
 - New visitors want to easily find out what or who the site is for.
 - New visitors want to easily navigate the website.
 - Visitors want to register for the website.
 - Users want to easily add their own recipes.
 - Users want to find others' recipes.

### Features:
- Responsive and user friendly interface.
- Easy navigation menu.
- Intuitive search feature.
- Simple and intuitive forms.
- Informative form validation feedback.
- Users can easily add or edit recipes.
- Users can edit their profile.

### Structure:
 - All pages will have a top navigation bar.
 - Main content will be centered horizontally and vertically.
 - Search results will be displayed in a grid of recipe cards.
 - Profile pages will feature that users' recipes.
 - Dedicated page for each recipe to allow bookmarking of recipes.


### Skeleton:
###### Wireframes:
__Home Page__ ![Home_page](wireframes/HOME.png)
__Profile Page__ ![Profile_page](wireframes/PROFILE.png)
__Search Page__ ![Search_page](wireframes/SEARCH.png)

### Surface:
 - I chose a simple color pallete featuring tones that resemble natural food colors.
 - I used intuitive colors for call to action buttons and form buttons.
 - I used the Material Design Bootstrap CSS framework which includes Roboto as a default font and implements material design button effects. This helps to make the site intuitive and user friendly.


### Database Planning:

The database will contain 2 collections: Users and Recipes.

[Link to database schema](DATABASE.MD)

### Existing Features: 
 - 


### Features to implement:
 - Email verification
 - cook sharing feature:
   - users can offer to cook or accept other users' offers.
   - offers are based on location and users can view them on a map.
 - recipe favourites:
   - users can save recipes to their favourites collection
   - users can view other users' favourites.

### Technologies Used:
- HTML
- CSS
- Javascript
- Python (Flask)
- WTForms/Flask-WTforms for server-side form validation
- MDBootstrap

### Issues:
 - ##### Dynamic number of input fields and WTForms validation:
   - For the recipe form I want the user to be able to dyncamically add and remove ingredients while still being able to validate the input with WTForms. I adapted the code found in [this guide](https://www.rmedgar.com/blog/dynamic-fields-flask-wtf/) to render inputs with the correct attributes to allow for WTForms validation.
 - ##### 413 error handling:
  - When a user uploads a file that is larger than the limit set in flask (MAX_CONTENT_LENGTH), the connection is aborted before the error is handled properly. The browser displays a default "ERR_CONNECTION_ABORTED" message. This is the case with a local werkzeug development server, with debug on or off and also when deployed to heroku using gunicorn in production mode.
  - Solution: I couldn't find a way to get the server to handle the 413 and redirect instead of showing the default browser error page so I decided to validate the file size and extension in Javascript. I added an event listener to the file input which would display an error and disable the form submit button if the user selected a file over 2MB or a file that didn't have a .jpg, .jpeg or .png extension.
