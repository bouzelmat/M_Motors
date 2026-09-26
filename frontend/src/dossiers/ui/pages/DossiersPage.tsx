// Dashboard page (protected route)

import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Button,
  Paper,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { useAuthStore } from '../../../auth/ui/hooks/useAuth';

export function DossiersPage() {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!isAuthenticated || !user) {
    return null;
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1">
          Tableau de bord
        </Typography>
        <Button variant="outlined" color="primary" onClick={handleLogout}>
          Déconnexion
        </Button>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Bienvenue, {user.first_name} {user.last_name}
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Email: {user.email}
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Rôle: {user.role}
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Mes dossiers
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Gérez vos dossiers M-Motors
              </Typography>
              <Button
                variant="contained"
                sx={{ mt: 2 }}
                onClick={() => navigate('/dossiers/create')}
              >
                Créer un dossier
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {user.role === 'ADMIN' && (
          <Grid item xs={12}>
            <Card sx={{ bgcolor: 'action.hover', border: '1px dashed grey' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom color="primary">
                  Administration des véhicules
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Espace de gestion réservé aux administrateurs M-Motors.
                </Typography>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<AddIcon />}
                  onClick={() => navigate('/admin/vehicles/new')}
                >
                  Ajouter un véhicule
                </Button>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Container>
  );
}