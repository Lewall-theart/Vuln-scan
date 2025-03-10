import os
import sys
import subprocess
import shutil
from datetime import date

today = date.today()
stringtoday = today.strftime("%b-%d-%Y")

PURPLE = '\033[1;35m'
RED = '\033[1;31m'
BLUE = '\033[1;38;5;37m'
DBLUE = '\033[36m'
YELLOW2 = '\033[1;38;5;172m'
GRAY = '\033[38;5;116m'
YELLOW = '\033[38;5;172m'
RED2 = '\033[1;38;5;160m'
CYAN = '\033[1;92m'
ENDCOLOR = '\033[0m'


if os.geteuid() == 0:
    print(RED + 'You are running as root!' + ENDCOLOR)

else:
    print(RED + 'You need to be root to run this program. Exiting...' + ENDCOLOR)
    sys.exit(1)


result = subprocess.run("which nmap", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if result.returncode == 0:
    pass
else:
    print("nmap is not installed. Install it with sudo apt install nmap")


if not os.path.exists('my_reports'):
    os.makedirs('my_reports')

def move_reports(file_name):
    os.rename(file_name, os.path.join('my_reports', file_name))


def run_and_save(command, output_file):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode == 0:
        print(DBLUE + result.stdout.decode("utf-8") + ENDCOLOR)
        print(CYAN + 'SCAN PERFORMED SUCCESFULLY' + ENDCOLOR)

    else:
        print(RED + "Failed to run the command. Error message:" + ENDCOLOR)
        print(result.stderr.decode("utf-8"))

    saveit = input("save the result?(y/n): ")
    if saveit == 'y':
        output_path = os.path.join('my_reports', f"{output_file}.txt")
        with open(output_path, "w") as file:
            file.write(result.stdout.decode("utf-8"))
        print(RED + f'Command output has been saved to {output_path}!' + ENDCOLOR)

    else:
        print(RED + 'Result not saved!' + ENDCOLOR)


def install_owasp_nettacker():
    git_clone_command = ["git", "clone", "https://github.com/OWASP/Nettacker.git"]

    try:
        print(RED + "Cloning OWASP Nettacker from GitHub..." + ENDCOLOR)
        subprocess.check_output(git_clone_command)
        print(RED + "Cloning completed." + ENDCOLOR)
    except subprocess.CalledProcessError as e:
        print(RED + f"Error while cloning OWASP Nettacker: {e}" + ENDCOLOR)
        sys.exit(1)

    try:
        print(RED + "Installing OWASP Nettacker dependencies..." + ENDCOLOR)
        output = subprocess.run('pip3 install -r Nettacker/requirements.txt', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(output.stdout.decode("utf-8"))
        print(RED + "Installation completed." + ENDCOLOR)
    except subprocess.CalledProcessError as e:
        print(RED + f"Error while installing OWASP Nettacker dependencies: {e}" + ENDCOLOR)
        sys.exit(1)


def run_owasp_nettacker(target_ip):
    command = f"python3 Nettacker/nettacker.py -i {target_ip} --profile vuln,information_gathering -o Nettacker--{target_ip}--{stringtoday}.html --graph d3_tree_v2_graph"

    try:
        print(BLUE + f"Starting OWASP Nettacker on target: {target_ip}" + ENDCOLOR)
        output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(BLUE + "OWASP Nettacker scan completed." + ENDCOLOR)
        print(output.stdout.decode("utf-8"))
        print(YELLOW + 'Press 8 to view reports' + ENDCOLOR)

    except subprocess.CalledProcessError as e:
        print(RED + f"Error while running OWASP Nettacker: {e}" + ENDCOLOR)
        sys.exit(1)


def install_docker():
    if subprocess.run(['which', 'docker'], stdout=subprocess.PIPE).returncode == 0:
        print(RED+'Docker is already installed'+ENDCOLOR)
        return

    subprocess.run(['sudo', 'apt', 'install', '-y', 'docker.io'])

    if subprocess.run(['which', 'docker'], stdout=subprocess.PIPE).returncode == 0:
        print(RED+'Docker is installed!'+ENDCOLOR)
    else:
        print(RED+'Failed to install Docker'+ENDCOLOR)
        return


def download_zap_docker_image():
    if subprocess.run(['docker', 'images', '-q', 'owasp/zap2docker-stable'], stdout=subprocess.PIPE).stdout.strip():
        print(RED+'OWASP Zap is available'+ENDCOLOR)
        return

    subprocess.run(['docker', 'pull', 'owasp/zap2docker-stable'])

    if subprocess.run(['docker', 'images', '-q', 'owasp/zap2docker-stable'], stdout=subprocess.PIPE).stdout.strip():
        print(RED+'OWASP Zap downloaded'+ENDCOLOR)
    else:
        print(RED+'Failed to download OWASP Zap'+ENDCOLOR)

def run_zap_scan(target_url,switch):
    out = target_url.split("//")[1]
    if switch == "0":
        command = f'sudo docker run -v $(pwd):/zap/wrk/:rw -t owasp/zap2docker-stable zap-baseline.py -t {target_url} -g gen.conf -r ZAP-basic--{out}--{stringtoday}.html'
        print(RED + "Basic scanning started..." + ENDCOLOR)
        subprocess.run(command, shell=True)
        print(CYAN + 'SCAN PERFORMED SUCCESFULLY' + ENDCOLOR)
        print(YELLOW + 'Press 8 to view reports' + ENDCOLOR)

    elif switch == "1":
        command = f'sudo docker run -v $(pwd):/zap/wrk/:rw -t owasp/zap2docker-stable zap-full-scan.py -t {target_url} -g gen.conf -r ZAP-full--{out}--{stringtoday}.html'
        print(RED + "Full scanning started..." + ENDCOLOR)
        subprocess.run(command, shell=True)
        print(CYAN + 'SCAN PERFORMED SUCCESFULLY' + ENDCOLOR)
        print(YELLOW + 'Press 8 to view reports' + ENDCOLOR)

    else:
        print("Invalid choice, try again")

def nmap_os_scan(IPadress):
    command = ["sudo", "nmap", "-O", "-Pn", "--fuzzy", f"{IPadress}"]
    result = subprocess.run(command, capture_output=True, text=True)
    output_lines = result.stdout.split("\n")
    os_detected = False
    for line in output_lines:
        if "Aggressive" in line:
            os_detected = True
        if os_detected:
            print(DBLUE + line + ENDCOLOR)

    print(CYAN + 'SCAN PERFORMED SUCCESFULLY' + ENDCOLOR)
    save_output = input(f"{CYAN}Do you want to save the output to a file? (y/n): {ENDCOLOR}")

    if save_output.lower() == "y":

        output_filename = "OS Guessing--" + IPadress +'--'+ stringtoday

        output_path = os.path.join('my_reports', output_filename)
        with open(output_path, "w") as file:
            file.write(result.stdout)

        print(RED + f"Output saved to {output_path} successfully!" + ENDCOLOR)
    else:
        print(RED + "Output not saved." + ENDCOLOR)



######################################################################################
print(YELLOW+ '''
  --------------------------------------------------------
  | vulnerability scanner and information gathering tool |
  --------------------------------------------------------
    ''' + ENDCOLOR)

def menu():
    print(BLUE + '0: Help' + ENDCOLOR)
    print(BLUE + '1: Check availability' + ENDCOLOR)
    print(BLUE + '2: DNS enumeration' + ENDCOLOR)
    print(BLUE + '3: OS detection' + ENDCOLOR)
    print(BLUE + '4: Service and version detection' + ENDCOLOR)
    print(BLUE + '5: Vulnerability check with vulners ' + ENDCOLOR)
    print(BLUE + '6: OWASP ZAP' + ENDCOLOR)
    print(BLUE + '7: OWASP Nettacker' + ENDCOLOR)
    print(BLUE + '8: View reports' + ENDCOLOR)
    print(BLUE + '9: Exit program' + ENDCOLOR)
    print(BLUE +'10:Remove program' + ENDCOLOR)
    print(BLUE + '-------------------' + ENDCOLOR)

def option0():
    print(RED+"Welcome to help menu"+ENDCOLOR)
    print(YELLOW2 + 'target: ' + ENDCOLOR + PURPLE+'                     example.com or 192.168.1.100'+ENDCOLOR)
    print(YELLOW2 + 'target domain:'+ENDCOLOR + PURPLE+'               example.com or trythis.org'+ENDCOLOR)
    print(YELLOW2 + 'target domain with protocol:' + ENDCOLOR + PURPLE+' https://example.com or http://trythis.org'+ENDCOLOR)
    print('')
    print(YELLOW2 + '1: ' + ENDCOLOR + '-TCP SYN ping is useful for discovering alive hosts protected by a stateful firewall')
    print(YELLOW2 + '2: ' + ENDCOLOR + GRAY+'-Uses a perl script to enumerate DNS information of a domain and to discover non-contiguous ip blocks. \n    The main purpose of Dnsenum is to gather as much information as possible about a domain.'+ENDCOLOR)
    print(YELLOW2 + '3: ' + ENDCOLOR + '-Nmap sends TCP and UDP packets to a particular port, and then analyze its response. It compares this response\n    to a database of 2600 operating systems, and return information on the OS (and version) of a host.')
    print(YELLOW2 + '4: ' + ENDCOLOR + GRAY+'-Starts Nmap scan on a given target and probe open ports to determine service/version info'+ENDCOLOR)
    print(YELLOW2 + '5: ' + ENDCOLOR + 'The vulners script sends CPE descriptions of discovered services by Nmap to the vulners.com vulnerability database API and reports known CVEs in those services.')
    print(YELLOW2 + '6: ' + ENDCOLOR + GRAY+'-The OWASP Zed Attack Proxy (ZAP) is one of the world’s most popular free security tools and is actively maintained by a dedicated international team of volunteers.\n    It can help you automatically find security vulnerabilities in your web applications while you are developing and testing your applications.\n    It is also a great tool for experienced pentesters to use for manual security testing.'+ENDCOLOR)
    print(YELLOW2 + '7: ' + ENDCOLOR + '-OWASP Nettacker project is created to automate information gathering, vulnerability scanning and eventually generating a report for networks, including services,\n    bugs, vulnerabilities, misconfigurations, and other information.')

    print(YELLOW2 + '-------------------' + ENDCOLOR)


def option3():
    print("OS detection")
    IPadress = input(f"{PURPLE}target: {ENDCOLOR}")
    nmap_os_scan(IPadress)    

def option1():
    print("Check availability")
    IPadress = input(f"{PURPLE}target: {ENDCOLOR}")
    command = f"sudo nping --tcp -p 21,22,23,25,53,80,110,143,443,465,587,993,995,1433,1521,3306,3389,5432,5900,8080 --delay 1s -H --count 2 --flags syn {IPadress}"
    run_and_save(command,"Ping target--" + IPadress +'--'+ stringtoday)


def option4():
    print("Service and version detection")
    IPadress = input(f"{PURPLE}target: {ENDCOLOR}")
    command = f"sudo nmap -sS -sV -T2 {IPadress}"
    run_and_save(command, "Service and version detection--" + IPadress +'--'+ stringtoday)

def option6():
    print("OWASP ZAP")
    install_docker()
    download_zap_docker_image()

    inp = input(PURPLE + 'target URL with protocol: ' + ENDCOLOR)
    out = inp.split("//")[1]
    print(BLUE + "0 : Basic scan" + ENDCOLOR)
    print(BLUE + "1 : Full scan" + ENDCOLOR)
    switch = input(f"{PURPLE}Scan method: {ENDCOLOR}")

    run_zap_scan(inp,switch)
    if switch == "0":
        move_reports(f'ZAP-basic--{out}--{stringtoday}.html')
    elif switch == "1":
        move_reports(f'ZAP-full--{out}--{stringtoday}.html')

def option7():
    print("OWASP Nettacker")
    IPadress = input(f"{PURPLE}target: {ENDCOLOR}")
    isExist = os.path.exists("Nettacker")

    if not isExist:
        install_owasp_nettacker()
        run_owasp_nettacker(IPadress)
        move_reports(f'Nettacker--{IPadress}--{stringtoday}.html')

    else:
        print(RED + "OWASP Nettacker installed" + ENDCOLOR)
        run_owasp_nettacker(IPadress)
        move_reports(f'Nettacker--{IPadress}--{stringtoday}.html')

def option10():
    delete = input(f"{RED}Do you want to delete the program?(y/n): {ENDCOLOR}")
    if delete == 'y':
        print(RED + f'Deleting docker image...' + ENDCOLOR)

        image = 'owasp/zap2docker-stable'
        if subprocess.run(['docker', 'images', '-q', image], stdout=subprocess.PIPE).stdout.strip():
            os.system(f"docker rmi -f {image}")
            print(f"{image} image has been removed!")
            print(RED + f"Removing Docker..." + ENDCOLOR)
            os.system("apt-get remove -y docker.io")
            print(RED + f"Docker has been removed..." + ENDCOLOR)

        else:
            print(f"{image} image does not exist.")

        print(RED + f'Deleting files...' + ENDCOLOR)
        dir_path = os.path.dirname(os.path.realpath(__file__))

        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path} due to {e}")

        os.unlink(os.path.realpath(__file__))


def option2():
    print("DNS Enumeration selected")
    domain = input(f"{PURPLE} target domain:{ENDCOLOR}")
    command = f"dnsenum --noreverse {domain}"
    run_and_save(command, f"DNSenum--{domain}--{stringtoday}.txt")

def option8():
    subprocess.run('sudo -u $(logname) xdg-open my_reports', shell=True)
    print(RED + 'Your reports are opened!' + ENDCOLOR)

def option5():
    IPadress = input(f"{PURPLE}target: {ENDCOLOR}")
    command = f"sudo nmap -sV --script vulners {IPadress}"
    run_and_save(command, "Nmap vulners--" + IPadress + '--' + stringtoday)

while True:
    menu()
    choice = input(f"{YELLOW2}Enter your choice: {ENDCOLOR}")

    if choice == "0":
        option0()
    elif choice == "1":
        option1()
    elif choice == "2":
        option2()
    elif choice == "3":
        option3()
    elif choice == "4":
        option4()
    elif choice == "5":
        option5()
    elif choice == "6":
        option6()
    elif choice == "7":
        option7()
    elif choice == "8":
        option8()
    elif choice == "9":
        print(RED + 'Exiting...' + ENDCOLOR)
        break
    elif choice == "10":
        option10()
    else:
        print(RED + "Invalid choice. Please try again." + ENDCOLOR)
