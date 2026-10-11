import React, { useState } from "react";
import {
  Box,
  Drawer,
  AppBar,
  Button,
  Toolbar,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Avatar,
  Stack,
  useTheme,
  useMediaQuery,
} from "@mui/material";
import DashboardIcon from "@mui/icons-material/Dashboard";
import DirectionsCarIcon from "@mui/icons-material/DirectionsCar";
import FolderSharedIcon from "@mui/icons-material/FolderShared";
import MenuIcon from "@mui/icons-material/Menu";
import LogoutIcon from "@mui/icons-material/Logout";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuthStore } from "../../../auth/ui/hooks/useAuth";

const SIDEBAR_WIDTH = 260;

export const AdminLayout: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const menuItems = [
    { label: "Dossiers de souscription", path: "/admin/dossiers", icon: <FolderSharedIcon /> },
    { label: "Gestion des véhicules", path: "/admin/vehicles", icon: <DirectionsCarIcon /> },
  ];

  const sidebarContent = (
    <Box
      sx={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        backgroundColor: "#0E0E11",
        color: "#FFFFFF",
        p: 2.5,
      }}
    >
      {/* Brand Header */}
      <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, mb: 4, px: 1 }}>
        <Box
          sx={{
            width: 36,
            height: 36,
            borderRadius: 999,
            backgroundColor: theme.palette.accent?.location || "#3B82F6",
            color: "#FFFFFF",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <DashboardIcon sx={{ fontSize: 20 }} />
        </Box>
        <Typography variant="h6" sx={{ fontWeight: 800, color: "#FFFFFF", fontSize: "1.1rem" }}>
          M-MOTORS <Typography component="span" variant="caption" sx={{ color: "rgba(255,255,255,0.5)", ml: 0.5 }}>PRO</Typography>
        </Typography>
      </Box>

      {/* Navigation List */}
      <List sx={{ flex: 1, p: 0 }}>
        {menuItems.map((item) => {
          const isActive = location.pathname.startsWith(item.path);
          return (
            <ListItem key={item.path} disablePadding sx={{ mb: 1 }}>
              <ListItemButton
                component={Link}
                to={item.path}
                sx={{
                  borderRadius: 12,
                  backgroundColor: isActive ? "rgba(255, 255, 255, 0.12)" : "transparent",
                  color: isActive ? "#FFFFFF" : "rgba(255, 255, 255, 0.65)",
                  "&:hover": {
                    backgroundColor: "rgba(255, 255, 255, 0.08)",
                    color: "#FFFFFF",
                  },
                }}
              >
                <ListItemIcon sx={{ color: isActive ? "#FFFFFF" : "rgba(255, 255, 255, 0.65)", minWidth: 40 }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.label} primaryTypographyProps={{ fontWeight: isActive ? 700 : 500, fontSize: "0.9rem" }} />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      {/* Footer / Back to Site */}
      <Stack spacing={1.5} sx={{ pt: 2, borderTop: "1px solid rgba(255, 255, 255, 0.1)" }}>
        <Button
          fullWidth
          variant="outlined"
          startIcon={<ArrowBackIcon />}
          component={Link}
          to="/"
          sx={{
            color: "#FFFFFF",
            borderColor: "rgba(255, 255, 255, 0.2)",
            borderRadius: 999,
            "&:hover": {
              borderColor: "#FFFFFF",
              backgroundColor: "rgba(255, 255, 255, 0.05)",
            },
          }}
        >
          Retour au site
        </Button>
      </Stack>
    </Box>
  );

  return (
    <Box sx={{ display: "flex", minHeight: "100vh", backgroundColor: theme.palette.background?.alternate || "#F6F7F8" }}>
      {/* Topbar */}
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          width: { md: `calc(100% - ${SIDEBAR_WIDTH}px)` },
          ml: { md: `${SIDEBAR_WIDTH}px` },
          backgroundColor: theme.palette.background.paper,
          borderBottom: `1px solid ${theme.palette.border?.subtle || "rgba(17, 17, 19, 0.08)"}`,
          color: theme.palette.text.primary,
        }}
      >

        <Toolbar sx={{ justifyContent: "space-between" }}>
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => setMobileOpen(!mobileOpen)}
            sx={{ mr: 2, display: { md: "none" } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" fontWeight={700}>
            Administration M-MOTORS
          </Typography>
          <Stack direction="row" spacing={2} alignItems="center">
            <Avatar sx={{ width: 34, height: 34, backgroundColor: theme.palette.text.primary, fontSize: "0.875rem", fontWeight: 700 }}>
              AD
            </Avatar>
            <Typography variant="body2" fontWeight={600}>
              Admin
            </Typography>
            <IconButton color="inherit" aria-label="Déconnexion" title="Déconnexion" onClick={handleLogout}>
              <LogoutIcon />
            </IconButton>
          </Stack>
        </Toolbar>
      </AppBar>

      {/* Desktop Sidebar */}
      <Box
        component="nav"
        sx={{ width: { md: SIDEBAR_WIDTH }, flexShrink: { md: 0 } }}
      >
        {isMobile ? (
          <Drawer
            variant="temporary"
            open={mobileOpen}
            onClose={() => setMobileOpen(false)}
            ModalProps={{ keepMounted: true }}
            PaperProps={{ sx: { width: SIDEBAR_WIDTH } }}
          >
            {sidebarContent}
          </Drawer>
        ) : (
          <Drawer
            variant="permanent"
            PaperProps={{
              sx: {
                width: SIDEBAR_WIDTH,
                boxSizing: "border-box",
                borderRight: "none",
              },
            }}
            open
          >
            {sidebarContent}
          </Drawer>
        )}
      </Box>

      {/* Main Content Area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          minWidth: 0,
          p: 3,
          mt: 8,
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
};
