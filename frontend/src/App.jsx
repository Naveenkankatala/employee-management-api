import { useEffect, useState } from "react";
import "./App.css";

function App() {
  // =========================
  // STATE
  // =========================

  const [employees, setEmployees] = useState([]);

  // Users
  const [users, setUsers] = useState([]);
  const [showUserManagement, setShowUserManagement] = useState(false);

  // Login
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  // User role
  const [userRole, setUserRole] = useState(
    localStorage.getItem("user_role") || ""
  );

  // Current logged-in user ID
  const [currentUserId, setCurrentUserId] = useState(
    Number(localStorage.getItem("user_id")) || null
  );

  const [isLoggedIn, setIsLoggedIn] = useState(
    !!localStorage.getItem("access_token")
  );

  const [message, setMessage] = useState("");

  // Employee form
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [department, setDepartment] = useState("");
  const [salary, setSalary] = useState("");

  // Edit
  const [editingId, setEditingId] = useState(null);

  // Search
  const [search, setSearch] = useState("");

  // =========================
  // LOGIN
  // =========================

  const handleLogin = async (e) => {
    e.preventDefault();

    const formData = new URLSearchParams();

    formData.append("username", username);
    formData.append("password", password);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/login",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: formData,
        }
      );

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem(
          "access_token",
          data.access_token
        );

        localStorage.setItem(
          "user_role",
          data.role
        );

        localStorage.setItem(
          "user_id",
          data.user_id
        );

        setUserRole(data.role);
        setCurrentUserId(Number(data.user_id));

        setIsLoggedIn(true);
        setMessage("Login successful!");

        setUsername("");
        setPassword("");
      } else {
        setMessage(
          data.detail || "Invalid username or password"
        );
      }
    } catch (error) {
      setMessage("Could not connect to server");
    }
  };

  // =========================
  // GET EMPLOYEES
  // =========================

  const fetchEmployees = async () => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      setIsLoggedIn(false);
      setUserRole("");
      setEmployees([]);
      return;
    }

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/employees",
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (response.status === 401) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user_role");
        localStorage.removeItem("user_id");

        setIsLoggedIn(false);
        setUserRole("");
        setCurrentUserId(null);
        setEmployees([]);
        setUsers([]);

        setMessage("Session expired. Please login again.");
        return;
      }

      if (response.ok) {
        setEmployees(data.employees);
      } else {
        setMessage(
          data.detail || "Failed to fetch employees"
        );
      }
    } catch (error) {
      setMessage("Could not connect to server");
    }
  };

  // =========================
  // GET USERS
  // ADMIN ONLY
  // =========================

  const fetchUsers = async () => {
    const token = localStorage.getItem("access_token");

    if (!token || userRole !== "admin") {
      return;
    }

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/users",
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (response.status === 401) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user_role");
        localStorage.removeItem("user_id");

        setIsLoggedIn(false);
        setUserRole("");
        setCurrentUserId(null);

        setEmployees([]);
        setUsers([]);

        setMessage("Session expired. Please login again.");
        return;
      }

      if (response.status === 403) {
        setMessage("Admin access required");
        return;
      }

      if (response.ok) {
        setUsers(data.users);
      } else {
        setMessage(
          data.detail || "Failed to fetch users"
        );
      }
    } catch (error) {
      setMessage("Could not connect to server");
    }
  };

  // =========================
  // SHOW USER MANAGEMENT
  // =========================

  const handleUserManagement = () => {
    const newState = !showUserManagement;

    setShowUserManagement(newState);

    if (newState) {
      fetchUsers();
    }
  };

  // =========================
  // CHANGE USER ROLE
  // =========================

  const handleChangeRole = async (
    userId,
    currentRole
  ) => {
    // Prevent changing own role
    if (userId === currentUserId) {
      setMessage("You cannot change your own role");
      return;
    }

    const newRole =
      currentRole === "admin"
        ? "user"
        : "admin";

    const confirmChange = window.confirm(
      `Are you sure you want to change this user role to "${newRole}"?`
    );

    if (!confirmChange) {
      return;
    }

    const token = localStorage.getItem("access_token");

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/users/${userId}/role?role=${newRole}`,
        {
          method: "PUT",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (response.ok) {
        setMessage(
          "User role updated successfully!"
        );

        fetchUsers();
      } else {
        setMessage(
          data.detail ||
            "Failed to update user role"
        );
      }
    } catch (error) {
      setMessage("Could not connect to server");
    }
  };

  // =========================
  // DELETE USER
  // ADMIN ONLY
  // =========================

  const handleDeleteUser = async (
    userId,
    username
  ) => {
    // Prevent deleting yourself
    if (userId === currentUserId) {
      setMessage(
        "You cannot delete your own account"
      );
      return;
    }

    const confirmDelete = window.confirm(
      `Are you sure you want to delete user "${username}"?`
    );

    if (!confirmDelete) {
      return;
    }

    const token = localStorage.getItem("access_token");

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/users/${userId}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (response.ok) {
        setMessage(
          "User deleted successfully!"
        );

        fetchUsers();
      } else {
        setMessage(
          data.detail ||
            "Failed to delete user"
        );
      }
    } catch (error) {
      setMessage("Could not connect to server");
    }
  };

  // =========================
  // ADD EMPLOYEE
  // ADMIN ONLY
  // =========================

  const handleAddEmployee = async (e) => {
    e.preventDefault();

    const token = localStorage.getItem("access_token");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/employees",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            name,
            email,
            department,
            salary: Number(salary),
          }),
        }
      );

      const data = await response.json();

      if (response.ok) {
        setMessage(
          "Employee added successfully!"
        );

        clearForm();

        fetchEmployees();
      } else {
        setMessage(
          data.detail ||
            "Failed to add employee"
        );
      }
    } catch (error) {
      setMessage(
        "Could not connect to server"
      );
    }
  };

  // =========================
  // EDIT EMPLOYEE
  // =========================

  const handleEditEmployee = (employee) => {
    setEditingId(employee.id);

    setName(employee.name);
    setEmail(employee.email);
    setDepartment(employee.department);
    setSalary(employee.salary);

    setMessage("");

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  // =========================
  // UPDATE EMPLOYEE
  // ADMIN ONLY
  // =========================

  const handleUpdateEmployee = async (e) => {
    e.preventDefault();

    const token =
      localStorage.getItem(
        "access_token"
      );

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/employees/${editingId}`,
        {
          method: "PUT",
          headers: {
            "Content-Type":
              "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            name,
            email,
            department,
            salary: Number(salary),
          }),
        }
      );

      const data =
        await response.json();

      if (response.ok) {
        setMessage(
          "Employee updated successfully!"
        );

        clearForm();

        fetchEmployees();
      } else {
        setMessage(
          data.detail ||
            "Failed to update employee"
        );
      }
    } catch (error) {
      setMessage(
        "Could not connect to server"
      );
    }
  };

  // =========================
  // DELETE EMPLOYEE
  // ADMIN ONLY
  // =========================

  const handleDeleteEmployee = async (
    employeeId
  ) => {
    const confirmDelete =
      window.confirm(
        "Are you sure you want to delete this employee?"
      );

    if (!confirmDelete) {
      return;
    }

    const token =
      localStorage.getItem(
        "access_token"
      );

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/employees/${employeeId}`,
        {
          method: "DELETE",
          headers: {
            Authorization:
              `Bearer ${token}`,
          },
        }
      );

      const data =
        await response.json();

      if (response.ok) {
        setMessage(
          "Employee deleted successfully!"
        );

        fetchEmployees();
      } else {
        setMessage(
          data.detail ||
            "Failed to delete employee"
        );
      }
    } catch (error) {
      setMessage(
        "Could not connect to server"
      );
    }
  };

  // =========================
  // CLEAR FORM
  // =========================

  const clearForm = () => {
    setName("");
    setEmail("");
    setDepartment("");
    setSalary("");
    setEditingId(null);
  };

  // =========================
  // CANCEL EDIT
  // =========================

  const handleCancelEdit = () => {
    clearForm();
    setMessage("");
  };

  // =========================
  // LOAD EMPLOYEES
  // =========================

  useEffect(() => {
    if (isLoggedIn) {
      fetchEmployees();
    }
  }, [isLoggedIn]);

  // =========================
  // LOGOUT
  // =========================

  const handleLogout = () => {
    localStorage.removeItem(
      "access_token"
    );

    localStorage.removeItem(
      "user_role"
    );

    localStorage.removeItem(
      "user_id"
    );

    setUserRole("");
    setCurrentUserId(null);
    setIsLoggedIn(false);

    setEmployees([]);
    setUsers([]);

    setShowUserManagement(false);

    clearForm();

    setSearch("");
    setMessage("");
  };

  // =========================
  // SEARCH EMPLOYEES
  // =========================

  const filteredEmployees =
    employees.filter(
      (employee) => {
        const searchText =
          search.toLowerCase();

        return (
          employee.name
            .toLowerCase()
            .includes(searchText) ||

          employee.email
            .toLowerCase()
            .includes(searchText) ||

          employee.department
            .toLowerCase()
            .includes(searchText)
        );
      }
    );

  // =========================
  // LOGIN PAGE
  // =========================

  if (!isLoggedIn) {
    return (
      <div className="login-page">

        <div className="login-overlay"></div>

        <div className="login-card">

          <div className="login-icon">
            👥
          </div>

          <h1>
            Employee{" "}
            <span>Management</span>
          </h1>

          <h2>
            Welcome Back
          </h2>

          <p className="login-subtitle">
            Please login to your account
          </p>

          <form
            onSubmit={handleLogin}
          >

            <div className="form-group">

              <label>
                Username
              </label>

              <div className="input-wrapper">

                <span className="input-icon">
                  👤
                </span>

                <input
                  type="text"
                  value={username}
                  onChange={(e) =>
                    setUsername(
                      e.target.value
                    )
                  }
                  placeholder="Enter username"
                  required
                />

              </div>

            </div>

            <div className="form-group">

              <label>
                Password
              </label>

              <div className="input-wrapper">

                <span className="input-icon">
                  🔒
                </span>

                <input
                  type="password"
                  value={password}
                  onChange={(e) =>
                    setPassword(
                      e.target.value
                    )
                  }
                  placeholder="Enter password"
                  required
                />

              </div>

            </div>

            <button
              className="btn btn-primary login-button"
              type="submit"
            >
              Login
            </button>

          </form>

          {message && (
            <div className="message">
              {message}
            </div>
          )}

        </div>

      </div>
    );
  }

  // =========================
  // DASHBOARD
  // =========================

  return (
    <div className="dashboard">

      {/* NAVBAR */}

      <nav className="navbar">

        <h1>
          Employee Management
        </h1>

        <div className="navbar-right">

          <span>
            Role:{" "}

            <strong>
              {userRole === "admin"
                ? "Admin"
                : "User"}
            </strong>
          </span>

          {userRole === "admin" && (
            <button
              className="btn"
              onClick={
                handleUserManagement
              }
            >
              {showUserManagement
                ? "Employees"
                : "User Management"}
            </button>
          )}

          <button
            className="btn"
            onClick={handleLogout}
          >
            Logout
          </button>

        </div>

      </nav>

      <main className="dashboard-content">

        {/* =================================
            USER MANAGEMENT
        ================================= */}

        {userRole === "admin" &&
        showUserManagement ? (

          <div className="table-card">

            <h2>
              User Management
            </h2>

            {message && (
              <div className="message">
                {message}
              </div>
            )}

            {users.length === 0 ? (

              <p>
                No users found.
              </p>

            ) : (

              <table className="employee-table">

                <thead>

                  <tr>

                    <th>
                      ID
                    </th>

                    <th>
                      Username
                    </th>

                    <th>
                      Role
                    </th>

                    <th>
                      Actions
                    </th>

                  </tr>

                </thead>

                <tbody>

                  {users.map(
                    (user) => (

                      <tr
                        key={user.id}
                      >

                        <td>
                          {user.id}
                        </td>

                        <td>
                          {user.username}
                        </td>

                        <td>
                          {user.role}
                        </td>

                        <td>

                          {user.id ===
                          currentUserId ? (

                            <span>
                              Current User
                            </span>

                          ) : (

                            <>

                              <button
                                className="btn btn-edit"
                                onClick={() =>
                                  handleChangeRole(
                                    user.id,
                                    user.role
                                  )
                                }
                              >
                                {user.role ===
                                "admin"
                                  ? "Make User"
                                  : "Make Admin"}
                              </button>

                              <button
                                className="btn btn-delete"
                                onClick={() =>
                                  handleDeleteUser(
                                    user.id,
                                    user.username
                                  )
                                }
                              >
                                Delete
                              </button>

                            </>

                          )}

                        </td>

                      </tr>

                    )
                  )}

                </tbody>

              </table>

            )}

          </div>

        ) : (

          <>
            {/* =================================
                STATISTICS
            ================================= */}

            <div className="stats">

              <div className="stat-card">

                <h3>
                  Total Employees
                </h3>

                <p>
                  {employees.length}
                </p>

              </div>

              <div className="stat-card">

                <h3>
                  Departments
                </h3>

                <p>
                  {
                    new Set(
                      employees.map(
                        (employee) =>
                          employee.department
                      )
                    ).size
                  }
                </p>

              </div>

              <div className="stat-card">

                <h3>
                  Average Salary
                </h3>

                <p>
                  ₹
                  {employees.length >
                  0
                    ? Math.round(
                        employees.reduce(
                          (
                            total,
                            employee
                          ) =>
                            total +
                            Number(
                              employee.salary
                            ),
                          0
                        ) /
                          employees.length
                      )
                    : 0}
                </p>

              </div>

            </div>

            {/* =================================
                ADD / EDIT FORM
                ADMIN ONLY
            ================================= */}

            {userRole ===
              "admin" && (

              <div className="form-card">

                <h2>
                  {editingId
                    ? "Edit Employee"
                    : "Add Employee"}
                </h2>

                <form
                  onSubmit={
                    editingId
                      ? handleUpdateEmployee
                      : handleAddEmployee
                  }
                >

                  <div className="form-grid">

                    <div className="form-group">

                      <label>
                        Name
                      </label>

                      <input
                        type="text"
                        value={name}
                        onChange={(e) =>
                          setName(
                            e.target.value
                          )
                        }
                        placeholder="Enter name"
                        required
                      />

                    </div>

                    <div className="form-group">

                      <label>
                        Email
                      </label>

                      <input
                        type="email"
                        value={email}
                        onChange={(e) =>
                          setEmail(
                            e.target.value
                          )
                        }
                        placeholder="Enter email"
                        required
                      />

                    </div>

                    <div className="form-group">

                      <label>
                        Department
                      </label>

                      <input
                        type="text"
                        value={department}
                        onChange={(e) =>
                          setDepartment(
                            e.target.value
                          )
                        }
                        placeholder="Enter department"
                        required
                      />

                    </div>

                    <div className="form-group">

                      <label>
                        Salary
                      </label>

                      <input
                        type="number"
                        value={salary}
                        onChange={(e) =>
                          setSalary(
                            e.target.value
                          )
                        }
                        placeholder="Enter salary"
                        required
                      />

                    </div>

                  </div>

                  <button
                    className="btn btn-primary"
                    type="submit"
                  >
                    {editingId
                      ? "Update Employee"
                      : "Add Employee"}
                  </button>

                  {editingId && (
                    <button
                      className="btn btn-cancel"
                      type="button"
                      onClick={
                        handleCancelEdit
                      }
                    >
                      Cancel
                    </button>
                  )}

                </form>

                {message && (
                  <div className="message">
                    {message}
                  </div>
                )}

              </div>
            )}

            {/* =================================
                USER MESSAGE
            ================================= */}

            {userRole !==
              "admin" &&
              message && (

              <div className="message">
                {message}
              </div>
            )}

            {/* =================================
                EMPLOYEE TABLE
            ================================= */}

            <div className="table-card">

              <h2>
                Employees
              </h2>

              <div className="search-container">

                <input
                  type="text"
                  placeholder="Search by name, email or department..."
                  value={search}
                  onChange={(e) =>
                    setSearch(
                      e.target.value
                    )
                  }
                />

              </div>

              {filteredEmployees.length ===
              0 ? (

                <p>
                  {search
                    ? "No employees match your search."
                    : "No employees found."}
                </p>

              ) : (

                <table className="employee-table">

                  <thead>

                    <tr>

                      <th>
                        ID
                      </th>

                      <th>
                        Name
                      </th>

                      <th>
                        Email
                      </th>

                      <th>
                        Department
                      </th>

                      <th>
                        Salary
                      </th>

                      {userRole ===
                        "admin" && (
                        <th>
                          Actions
                        </th>
                      )}

                    </tr>

                  </thead>

                  <tbody>

                    {filteredEmployees.map(
                      (employee) => (

                        <tr
                          key={
                            employee.id
                          }
                        >

                          <td>
                            {employee.id}
                          </td>

                          <td>
                            {employee.name}
                          </td>

                          <td>
                            {employee.email}
                          </td>

                          <td>
                            {
                              employee.department
                            }
                          </td>

                          <td>
                            ₹
                            {
                              employee.salary
                            }
                          </td>

                          {userRole ===
                            "admin" && (
                            <td>

                              <button
                                className="btn btn-edit"
                                onClick={() =>
                                  handleEditEmployee(
                                    employee
                                  )
                                }
                              >
                                Edit
                              </button>

                              <button
                                className="btn btn-delete"
                                onClick={() =>
                                  handleDeleteEmployee(
                                    employee.id
                                  )
                                }
                              >
                                Delete
                              </button>

                            </td>
                          )}

                        </tr>

                      )
                    )}

                  </tbody>

                </table>

              )}

            </div>

          </>

        )}

      </main>

    </div>
  );
}

export default App;