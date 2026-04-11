import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const PublicLayout = () => import("@/layouts/PublicLayout.vue");
const LandingPortal = () => import("@/views/public/LandingPortal.vue");
const HomeView = () => import("@/views/public/Home.vue");
const AboutUs = () => import("@/views/public/AboutUs.vue");
const ContactUs = () => import("@/views/public/ContactUs.vue");
const PhotoGallery = () => import("@/views/public/PhotosGallery.vue");
const Catalog = () => import("@/views/public/Catalog.vue");
const ConfiguracionAdmin = () => import("@/views/admin/config.vue");

const AppLayout = () => import("@/layouts/AppLayout.vue");
const AdminLayout = () => import("@/layouts/AdminLayout.vue");
const AuthLayout = () => import("@/layouts/AuthLayout.vue");

const routes = [
  // ZONA PÚBLICA
  {
    path: "/",
    name: "landing-portal",
    component: LandingPortal, 
    meta: { hideNav: true }
  },

  {
    path: "/hospedaje",
    component: PublicLayout,
    children: [
      { path: "", name: "hospedaje-home", component: HomeView }, // El inicio de hospedaje
      { path: "about", name: "about", component: AboutUs },
      { path: "gallery", name: "gallery", component: PhotoGallery },
      { path: "rooms", name: "rooms", component: Catalog },
      { path: "contact", name: "contact", component: ContactUs },
    ],
  },

  // ZONA AUTH
  {
    path: "/auth",
    component: AuthLayout,
    children: [
      {
        path: "login",
        name: "login",
        component: () => import("@/views/auth/Login.vue"),
      },
      {
        path: "register",
        name: "register",
        component: () => import("@/views/auth/Register.vue"),
      },
    ],
  },

  // ZONA APP (CLIENTE)
  {
    path: "/app",
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: "",
        redirect: { name: "account-profile" },
      },
      {
        path: "profile",
        name: "account-profile",
        component: () => import("@/views/app/ProfileView.vue"),
      },
      // 🟢 NUEVA RUTA: CONFIGURACIÓN 🟢
      {
        path: "settings",
        name: "account-settings",
        component: () => import("@/views/app/SettingsView.vue"),
      },
      // -------------------------------
      {
        path: "bookings",
        name: "account-bookings",
        component: () => import("@/views/app/BookingsView.vue"),
      },
      {
        path: "notifications",
        name: "account-notifications",
        component: () => import("@/views/app/NotificationsView.vue"),
      },
      {
        path: "booking-detail/:id",
        name: "account-booking-detail",
        component: () => import("@/views/app/BookingDetail.vue"),
      },
    ],
  },

  // ZONA ADMIN
  {
    path: "/admin",
    component: AdminLayout,
    meta: { requiresAuth: true, isAdmin: true, hideNav: true },
    children: [
      {
        path: "",
        redirect: { name: "admin-dashboard" },
      },
      {
        path: "dashboard",
        name: "admin-dashboard",
        component: () => import("@/views/admin/DashboardView.vue"),
      },
      {
        path: "rooms",
        name: "admin-rooms",
        component: () => import("@/views/admin/RoomsManager.vue"),
      },
      {
        path: "bookings",
        name: "admin-bookings",
        component: () => import("@/views/admin/BookingsManager.vue"),
      },
      {
        path: "users",
        name: "admin-users",
        component: () => import("@/views/admin/UsersManager.vue"),
      },
      {
        path: "gallery",
        name: "admin-gallery",
        component: () => import("@/views/admin/GalleryManager.vue"),
      },
      {
      path: 'configuracion',
      name: 'admin-config',
      component: ConfiguracionAdmin,
      // Aquí podrías tener tus validaciones de rol, por ejemplo:
      // meta: { requiresAuth: true, role: 'admin' }
      }
    ],
  },

  // 404
  {
    path: "/:pathMatch(.*)*",
    name: "not-found",
    meta: { hideNav: true },
    component: () => import("@/views/NotFound.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0, behavior: "smooth" };
  },
});

// GUARDIA DE NAVEGACIÓN
router.beforeEach((to, from, next) => {
  const auth = useAuthStore();

  // 1. Ruta protegida y no está logueado → al login
  if (to.meta.requiresAuth && !auth.isLogged) {
    return next({ name: "login" });
  }

  // 2. Ruta de admin y no es admin → al home
  if (to.meta.isAdmin && !auth.isAdmin) {
    return next({ name: "hospedaje-home" }); // 🟢 Cambié "home" a "hospedaje-home" porque "home" no existía en tus rutas
  }

  // 3. Ya logueado intenta entrar al login/register → redirigir según rol
  if ((to.name === "login" || to.name === "register") && auth.isLogged) {
    if (auth.isAdmin) {
      return next({ name: "admin-dashboard" });
    }
    return next({ name: "account-profile" });
  }

  next();
});

export default router;