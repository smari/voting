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
import Election from './Election.vue'
import Simulate from './Simulate.vue'

const routes = [
  { path: '/election', component: Election },
  { path: '/simulate', component: Simulate }
]

var router = new VueRouter({ routes })
var app = new Vue({ router, el: "#app", render: h => h(App) })
