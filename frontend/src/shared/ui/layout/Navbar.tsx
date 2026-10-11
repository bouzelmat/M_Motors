import React, { useState } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Button,
  IconButton,
  Container,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  useTheme,
  useMediaQuery,
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import CloseIcon from "@mui/icons-material/Close";
import DirectionsCarIcon from "@mui/icons-material/DirectionsCar";
import PersonOutlineIcon from "@mui/icons-material/PersonOutline";
import LogoutIcon from "@mui/icons-material/Logout";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useScrolled } from "../hooks/useScrolled";
import { useAuthStore } from "../../../auth/ui/hooks/useAuth";

export const Navbar: React.FC = () => {
  const theme = useTheme();
  const isScrolled = useScrolled(40);
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    setMobileOpen(false);
    navigate("/login");
  };

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const navLinks = [
    { label: "Accueil", path: "/" },
    { label: "Catalogue", path: "/catalogue" },
    { label: "Simulateur LLD", path: "/simulator" },
    { label: "Espace Client", path: "/dashboard" },
  ];

  return (
    <AppBar
      position="fixed"
      elevation={0}
      sx={{
        height: 64,
        justifyContent: "center",
        backgroundColor: isScrolled
          ? theme.palette.glass?.bg || "rgba(255, 255, 255, 0.70)"
          : "transparent",
        backdropFilter: isScrolled ? "blur(20px)" : "none",
        WebkitBackdropFilter: isScrolled ? "blur(20px)" : "none",
        borderBottom: isScrolled
          ? `1px solid ${theme.palette.border?.subtle || "rgba(17, 17, 19, 0.08)"}`
          : "1px solid transparent",

        color: theme.palette.text.primary,
        transition: "all 250ms ease-out",
        zIndex: theme.zIndex.drawer + 1,
      }}
    >
      <Container maxWidth="xl">
        <Toolbar disableGutters sx={{ justifyContent: "space-between", minHeight: 64 }}>
          {/* Logo */}
          <Box
            component={Link}
            to="/"
            sx={{
              display: "flex",
              alignItems: "center",
              gap: 1.25,
              textDecoration: "none",
              color: theme.palette.text.primary,
            }}
          >
            <Box
              sx={{
                width: 38,
                height: 38,
                borderRadius: 999,
                backgroundColor: theme.palette.text.primary,
                color: "#FFFFFF",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <DirectionsCarIcon sx={{ fontSize: 22 }} />
            </Box>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 900,
                letterSpacing: "-0.03em",
                color: theme.palette.text.primary,
                fontSize: "1.25rem",
              }}
            >
              M-MOTORS
            </Typography>
          </Box>

          {/* Desktop Navigation Links */}
          {!isMobile && (
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              {navLinks.map((link) => {
                const isActive = location.pathname === link.path;
                return (
                  <Button
                    key={link.path}
                    component={Link}
                    to={link.path}
                    sx={{
                      color: isActive
                        ? theme.palette.text.primary
                        : theme.palette.text.secondary,
                      fontWeight: isActive ? 700 : 500,
                      px: 2,
                      py: 1,
                      borderRadius: 999,
                      "&:hover": {
                        color: theme.palette.text.primary,
                        backgroundColor: "rgba(17, 17, 19, 0.04)",
                      },
                    }}
                  >
                    {link.label}
                  </Button>
                );
              })}
            </Box>
          )}

          {/* Desktop Action Buttons */}
          {!isMobile && (
            <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
              {isAuthenticated ? (
                <Button
                  variant="outlined"
                  onClick={handleLogout}
                  startIcon={<LogoutIcon />}
                  size="small"
                  sx={{ borderRadius: 999 }}
                >
                  Déconnexion
                </Button>
              ) : (
                <Button
                  variant="outlined"
                  component={Link}
                  to="/login"
                  startIcon={<PersonOutlineIcon />}
                  size="small"
                  sx={{ borderRadius: 999 }}
                >
                  Connexion
                </Button>
              )}
              <Button
                variant="contained"
                color="primary"
                component={Link}
                to="/catalogue"
                size="small"
                sx={{ borderRadius: 999 }}
              >
                Voir les véhicules
              </Button>
            </Box>
          )}

          {/* Mobile Menu Icon */}
          {isMobile && (
            <IconButton
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ color: theme.palette.text.primary }}
            >
              {mobileOpen ? <CloseIcon /> : <MenuIcon />}
            </IconButton>
          )}
        </Toolbar>
      </Container>

      {/* Mobile Drawer */}
      <Drawer
        anchor="top"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        PaperProps={{
          sx: {
            top: 64,
            width: "100%",
            backgroundColor: theme.palette.background.default,
            p: 3,
            boxShadow: "0 20px 40px rgba(17, 17, 19, 0.1)",
          },
        }}
      >
        <List>
          {navLinks.map((link) => (
            <ListItem key={link.path} disablePadding>
              <ListItemButton
                component={Link}
                to={link.path}
                onClick={handleDrawerToggle}
                sx={{ borderRadius: 12, py: 1.5 }}
              >
                <ListItemText
                  primary={link.label}
                  primaryTypographyProps={{ fontWeight: 700, fontSize: "1.1rem" }}
                />
              </ListItemButton>
            </ListItem>
          ))}
          <ListItem disablePadding sx={{ mt: 1 }}>
            {isAuthenticated ? (
              <Button
                fullWidth
                variant="outlined"
                startIcon={<LogoutIcon />}
                onClick={handleLogout}
                size="large"
              >
                Déconnexion
              </Button>
            ) : (
              <Button
                fullWidth
                variant="outlined"
                component={Link}
                to="/login"
                onClick={handleDrawerToggle}
                startIcon={<PersonOutlineIcon />}
                size="large"
              >
                Connexion
              </Button>
            )}
          </ListItem>
          <ListItem disablePadding sx={{ mt: 2 }}>
            <Button
              fullWidth
              variant="contained"
              component={Link}
              to="/catalogue"
              onClick={handleDrawerToggle}
              size="large"
            >
              Voir le catalogue
            </Button>
          </ListItem>
        </List>
      </Drawer>
    </AppBar>
  );
};
