import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";

// --- IMPORTACIONES ESTÁTICAS ---
import PublicLayout from "@/layouts/PublicLayout.vue";
import LandingPortal from "@/views/public/LandingPortal.vue";
import HomeView from "@/views/public/Home.vue";
import AboutUs from "@/views/public/AboutUs.vue";
import ContactUs from "@/views/public/ContactUs.vue";
import PhotoGallery from "@/views/public/PhotosGallery.vue";
import Catalog from "@/views/public/Catalog.vue";


// Layouts Privados
import AppLayout from "@/layouts/AppLayout.vue";
import AdminLayout from "@/layouts/AdminLayout.vue";
import AuthLayout from "@/layouts/AuthLayout.vue";

const routes = [
  // ZONA PÚBLICA
  {
    path: "/",
    name: "landing-portal",
    component: LandingPortal, 
    meta: { hideNavbar: true }
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
      {
        path: "servicios",
        name: "servicios",
        component: () => import("@/views/ServiceSelection.vue"),
      }
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
    meta: { requiresAuth: true, isAdmin: true },
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
    ],
  },

  // 404
  {
    path: "/:pathMatch(.*)*",
    name: "not-found",
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
    return next({ name: "home" });
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