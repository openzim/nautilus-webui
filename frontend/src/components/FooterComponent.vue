<template>
  <footer class="footer d-flex justify-content-between mt-auto px-3 py-1 text-muted border-top">
    <div class="">
      Powered by
      <a href="https://github.com/openzim/nautilus" target="_blank" class="link-secondary"
        >Nautilus</a
      >
      &
      <a href="https://kiwix.org" target="_blank" class="link-secondary">Kiwix</a>
    </div>
    <div class="">Copyright {{ new Date().getFullYear() }}</div>
  </footer>
</template>

<style type="text/css">
.link-secondary:hover {
  cursor: pointer;
}
</style>
