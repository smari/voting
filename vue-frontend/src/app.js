import Vue from 'vue'
import VueRouter from 'vue-router'
import VueResource from 'vue-resource';
import BootstrapVue from 'bootstrap-vue'
Vue.use(VueRouter);
Vue.use(VueResource);
Vue.use(BootstrapVue);

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

import App from './App.vue'
import Main from './Main.vue'
import Intro from './Intro.vue'

const routes = [
  { path: '/', component: Intro },
  { path: '/calc', component: Main }
]

var router = new VueRouter({ routes })
var app = new Vue({ router, el: "#app", path: '/', render: h => h(App) })
