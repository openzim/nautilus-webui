<template>
  <div class="container">
    <a href="/">
      <div class="row justify-content-md-center gx-2">
        <div class="col-md-auto">
          <img
            alt="Nautilus Logo: A Nautilus shell."
            class="img-fluid"
            src="@/assets/logo.svg"
            width="55"
            height="45"
          />
        </div>
        <div class="col-md-auto align-middle">
          <p class="fs-1 fw-bold">Nautilus</p>
        </div>
      </div>
      <div class="row justify-content-md-center">
        <div class="col-md-auto">
          <p class="fs-5 fw-bold text-secondary">
            Just <span class="spot">Zim</span> Your Collection!
          </p>
        </div>
      </div>
    </a>
  </div>
</template>

<style scoped>
a,
a:active,
a:visited {
  color: var(--main-color);
  text-decoration: none;
}
.spot {
  color: var(--main-color);
}
</style>
