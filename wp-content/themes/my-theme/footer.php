<footer id="colophon" class="site-footer" role="contentinfo">
<div class="site-footer__inner">
<p>
&copy; <?php echo esc_html( gmdate( 'Y' ) ); ?>
<a href="<?php echo esc_url( home_url( '/' ) ); ?>">
<?php bloginfo( 'name' ); ?>
</a>.
<?php
printf(
/* translators: %s: WordPress link */
esc_html__( 'Proudly powered by %s.', 'my-theme' ),
'<a href="https://wordpress.org">WordPress</a>'
);
?>
</p>
</div>
</footer><!-- #colophon -->

</div><!-- #page -->

<?php wp_footer(); ?>
</body>
</html>

