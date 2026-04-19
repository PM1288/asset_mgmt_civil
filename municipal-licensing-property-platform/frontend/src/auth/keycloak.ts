import Keycloak from "keycloak-js";

const keycloak = new Keycloak({
  url: import.meta.env.VITE_KEYCLOAK_URL || `${window.location.origin}/auth`,
  realm: import.meta.env.VITE_KEYCLOAK_REALM || "municipal",
  clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID || "municipal-frontend"
});

export default keycloak;
