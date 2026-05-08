<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo( 'charset' ); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="profile" href="https://gmpg.org/xfn/11">
<?php wp_head(); ?>
</head>

<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<div id="page" class="site">

<a class="skip-link screen-reader-text" href="#posts">
<?php esc_html_e( 'Skip to content', 'my-theme' ); ?>
</a>

<header id="masthead" class="site-header" role="banner">
<div class="site-header__inner">

<div class="site-branding">
<?php if ( has_custom_logo() ) : ?>
<?php the_custom_logo(); ?>
<?php else : ?>
<p class="site-title">
<a href="<?php echo esc_url( home_url( '/' ) ); ?>" rel="home">
<?php bloginfo( 'name' ); ?>
</a>
</p>
<?php if ( get_bloginfo( 'description' ) ) : ?>
<p class="site-description"><?php bloginfo( 'description' ); ?></p>
<?php endif; ?>
<?php endif; ?>
</div><!-- .site-branding -->

<nav id="site-navigation" class="main-navigation" aria-label="<?php esc_attr_e( 'Primary menu', 'my-theme' ); ?>">
<?php
wp_nav_menu( [
'theme_location' => 'primary',
'menu_id'        => 'primary-menu',
'container'      => false,
'fallback_cb'    => false,
] );
?>
</nav><!-- #site-navigation -->

</div><!-- .site-header__inner -->
</header><!-- #masthead -->
