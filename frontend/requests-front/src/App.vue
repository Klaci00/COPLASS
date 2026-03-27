<template>
  <div id="app">
    <!-- Global Navigation Bar -->
    <nav>
      <router-link to="/">Home</router-link> |
      <router-link to="/login">Login</router-link>
      <router-link to="/dashboard">Dashboard</router-link>
      <router-link to="/access-right-requests">Access Right Requests</router-link>
    </nav>

    <!-- The current page content will render below the navigation -->
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
// No JavaScript needed here just for navigation links
</script>

<style>
/* Basic styling for the navigation bar */
nav {
  padding: 15px;
  background-color: #f8f9fa;
  margin-bottom: 20px;
  border-radius: 5px;
  text-align: center;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
  margin: 0 10px;
}

/* Vue automatically applies this class to the active link */
nav a.router-link-exact-active {
  color: #42b983; 
}

main {
  padding: 20px;
}
</style>