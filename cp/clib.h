#include<math.h>
#include<complex.h>
#include<fftw3.h>
#include<omp.h>

void compute_exch_field(double *spin, double *field, double *energy, double J, int nx, int ny, int nz, int xperiodic, int yperiodic);
double compute_exch_energy(double *spin, double J, int nx, int ny, int nz, int xperiodic, int yperiodic);

void compute_anis(double *spin, double *field, double Dx, double Dy, double Dz,
		int nxyz);

double compute_anis_energy(double *spin, double Dx, double Dy, double Dz,
		int nxyz);

void dmi_field(double *spin, double *field, double *energy,double D, int nx, int ny, int nz, int xperiodic, int yperiodic);
double dmi_energy(double *spin, double D, int nx, int ny, int nz,int xperiodic, int yperiodic);

void llg_rhs(double * dm_dt, double * spin, double * h, double *alpha,
		double gamma, int nxyz);

void llg_s_rhs(double * dm_dt, double * spin, double * h, double *alpha,
             double *chi, double gamma, int nxyz);


void compute_stt_field_c(double *spin, double *field, double jx, double jy, double jz,
                       double dx, double dy, double dz, int nx, int ny, int nz);
void llg_stt_rhs(double *dm_dt, double *m, double *h, double *h_stt, double *alpha,
                 double beta, double u0, double gamma, int nxyz);

void normalise(double *m, int nxyz);

//==========================================
//used for demag

typedef struct {
	int nx;
	int ny;
	int nz;
	double dx;
	double dy;
	double dz;
	int lenx;
	int leny;
	int lenz;

	int total_length;

	double *tensor_xx;
	double *tensor_yy;
	double *tensor_zz;
	double *tensor_xy;
	double *tensor_xz;
	double *tensor_yz;

	fftw_complex *Nxx;
	fftw_complex *Nyy;
	fftw_complex *Nzz;
	fftw_complex *Nxy;
	fftw_complex *Nxz;
	fftw_complex *Nyz;

	fftw_complex *Mx;
	fftw_complex *My;
	fftw_complex *Mz;
	fftw_complex *Hx;
	fftw_complex *Hy;
	fftw_complex *Hz;

	double *mx;
	double *my;
	double *mz;
	double *hx;
	double *hy;
	double *hz;

	double mu_s;

	//we need three plans
	fftw_plan tensor_plan;
	fftw_plan m_plan;
	fftw_plan h_plan;

} fft_demag_plan;

fft_demag_plan *create_plan(void);
void finalize_plan(fft_demag_plan *plan);
void init_plan(fft_demag_plan *plan, double mu_s, double dx, double dy,
		double dz, int nx, int ny, int nz);
void compute_fields(fft_demag_plan *plan, double *spin, double *field);
void exact_compute(fft_demag_plan *plan, double *spin, double *field);
double compute_demag_energy(fft_demag_plan *plan, double *spin, double *field);

//=========================================================
//=========================================================
//used for sode
typedef struct {
	int nxyz;

	double dt;
	double T;
	double gamma;
	double *mu_s;
	double coeff;
	double Q;

	double theta;
	double theta1;
	double theta2;

	double *dm1;
	double *dm2;
	double *eta;

} ode_solver;

void init_solver(ode_solver *s, double k_B, double theta, int nxyz, double dt, double gamma);
ode_solver *create_ode_plan(void);
void finalize_ode_plan(ode_solver *plan);
void run_step1(ode_solver *s, double *m, double *h, double *m_pred, double *T,
		double *alpha, double *mu_s_inv);
void run_step2(ode_solver *s, double *m_pred, double *h, double *m, double *T,
		double *alpha, double *mu_s_inv);

