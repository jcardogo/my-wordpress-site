# My WordPress Site

This repository contains the custom WordPress theme used for my personal website. It was originally created as an early hands-on project using GitHub Copilot and is intended to power a clean, modern content-focused site.

## Project Scope

This repository stores only the theme code (not a full WordPress installation).

Included path:

- wp-content/themes/my-theme

## Theme Summary

Theme name: My Theme

The theme provides:

- A responsive homepage with a hero section
- Card-based post grid layout
- Sticky dark header and primary navigation menu
- Featured image support for posts
- Accessible skip link and focus styles
- Clean footer with dynamic year and site name
- Student class booking and booking tracking forms integrated with a Python API

## Tech Stack

- WordPress 6.x
- PHP 7.4+
- Vanilla CSS (custom properties and responsive media queries)

## Repository Structure

- README.md: Project documentation
- wp-content/themes/my-theme/style.css: Theme metadata and all visual styles
- wp-content/themes/my-theme/functions.php: Theme setup and asset loading
- wp-content/themes/my-theme/header.php: Global site header and menu output
- wp-content/themes/my-theme/index.php: Homepage template and post loop
- wp-content/themes/my-theme/footer.php: Global footer markup
- python-booking-service/: Flask API for student booking/tracking with MSSQL
- python-booking-service/sql/: SQL Server schema and class seed scripts

## Local Development

1. Install WordPress locally (for example with Local, XAMPP, or Docker).
2. Copy the my-theme folder into your local WordPress installation under wp-content/themes/.
3. In the WordPress admin area, go to Appearance > Themes.
4. Activate My Theme.
5. Set Site Title and Tagline in Settings > General to populate the hero text.
6. Create or assign a menu to the Primary Menu location in Appearance > Menus.
7. Add posts and featured images to see the homepage card grid.

## Deployment

For shared hosting (such as Hostinger):

1. Upload the my-theme folder to wp-content/themes/ on the server.
2. Activate the theme from the WordPress admin panel.
3. Verify homepage rendering, navigation, and responsive behavior on mobile.

## Notes

- The current codebase is intentionally lightweight and does not include build tooling.
- This project can be extended with custom templates, customizer options, and Gutenberg block styles.
- For booking and tracking to work, start the Python service and SQL Server database described in python-booking-service/README.md.

## Author

Maintained by the repository owner.
