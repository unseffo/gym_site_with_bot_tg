<?php

$servername = "db1.ho.ua"; // or use the IP address if your MySQL server is on a different host
$username = "nosleepcoders";
$password = "usdthunter312";
$dbname = "nosleepcoders";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $name = $_POST["cf-name"];
    $email = $_POST["cf-email"];
    $message = $_POST["cf-message"];

    // Prepare and bind the SQL statement
    $stmt = $conn->prepare("INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)");
    $stmt->bind_param("sss", $name, $email, $message);

    // Execute the statement
    if ($stmt->execute()) {
        echo "Message sent successfully!";
    } else {
        echo "Error: " . $stmt->error;
    }

    // Close the statement
    $stmt->close();
}

$conn->close();
?>
